#!/usr/bin/env python3
"""
Xilinx 7-series 配置位流深度解析（L2 阶段）
输入：HEX 展开后的线性镜像（analyze_mcs.py / parse_mcs.py 产物 .bin）
用途：
  1) 解析同步字之后的 Type-1/Type-2 配置包，统计包类型/寄存器写入/命令(CMD)
  2) 跟踪 FAR/FDRI，按块类型(logic vs BRAM)粗估配置帧分布
  3) 明文字符串扫描：MicroBlaze/PicoBlaze/AXI/Ethernet/FTDI 等软核/外设线索
所有输出仅为静态证据，需与实物/JTAG 交叉验证。
"""
import sys
import collections
import math

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/workspace/zero0000-research/assets/firmware/20230825_s2056.bin"

data = open(PATH, "rb").read()
print(f"# 输入镜像: {PATH}")
print(f"镜像长度: {len(data)} 字节 ({len(data)/1024/1024:.3f} MiB)")

# ---------- 定位同步字 ----------
SYNC = bytes.fromhex("aa995566")
sync_off = data.find(SYNC)
sync_count = data.count(SYNC)
print(f"同步字 AA995566 偏移: 0x{sync_off:X}  出现次数: {sync_count}")
boot = data.find(bytes.fromhex("000000bb11220044"))
print(f"总线宽度/Boot 000000BB11220044 偏移: 0x{boot:X}")

# ---------- 配置包解析 ----------
REG = {0: "CRC", 1: "FAR", 2: "FDRI", 3: "FDRO", 4: "CMD", 5: "CTL0",
       6: "MASK", 7: "STAT", 8: "LOUT", 9: "COR0", 10: "MFWR", 11: "CBC",
       12: "IDCODE", 13: "AXSS", 14: "COR1", 16: "WBSTAR", 17: "TIMER",
       18: "RBCRC_SW", 22: "BOOTSTS", 24: "CTL1", 31: "BSPI"}
CMD = {0: "NULL", 1: "WCFG", 2: "MFW", 3: "DGHIGH/LFRM", 4: "RCFG", 5: "START",
       6: "RCAP", 7: "RCRC", 8: "AGHIGH", 9: "SWITCH", 10: "GRESTORE",
       11: "SHUTDOWN", 12: "GCAPTURE", 13: "DESYNC", 15: "IPROG",
       16: "CRCC", 17: "LTIMER", 18: "BSPI_READ", 19: "FALL_EDGE"}
OPC = {0: "NOP", 1: "READ", 2: "WRITE", 3: "resv"}

# 7-series 每帧字数（UG470）
WORDS_PER_FRAME = 101

def u32(off):
    return int.from_bytes(data[off:off+4], "big")

pos = sync_off + 4
end = len(data)
pkt_type_count = collections.Counter()   # 包头类型 1/2
opcode_count = collections.Counter()     # 操作码
reg_write_count = collections.Counter()  # 各寄存器写入次数
reg_write_words = collections.Counter()  # 各寄存器写入字数合计
cmd_seq = []                             # CMD 寄存器写入序列
reg_write_values = collections.defaultdict(list)  # 单字寄存器写入的值
nop_count = 0
last_reg = None

# FAR/FDRI 帧跟踪
fdri_writes = []       # (当前FAR, 字数)
far_writes = []        # FAR 值序列
current_far = None

parse_errors = 0
words_parsed = 0

while pos + 4 <= end:
    w = u32(pos)
    ptype = w >> 29
    words_parsed += 1
    if ptype == 1:  # Type-1
        pkt_type_count[1] += 1
        opcode = (w >> 27) & 0x3
        reg = (w >> 13) & 0x3FFF
        wc = w & 0x7FF
        opcode_count[opcode] += 1
        pos += 4
        if opcode == 0:  # NOP
            nop_count += 1
            last_reg = reg
            continue
        if opcode == 2:  # WRITE
            reg_write_count[reg] += 1
            reg_write_words[reg] += wc
            payload_off = pos
            # 读取写入的负载字（用于单字寄存器解码）
            if wc == 1 and payload_off + 4 <= end:
                val = u32(payload_off)
                if reg == 4:  # CMD
                    cmd_seq.append(val)
                elif reg == 1:  # FAR
                    current_far = val
                    far_writes.append(val)
                elif reg == 2:  # FDRI 单字（少见）
                    fdri_writes.append((current_far, 1))
                if reg in (0,4,5,6,9,11,12,13,14,16,17,24):
                    reg_write_values[reg].append(val)
            # 跳过负载
            pos += wc * 4
            last_reg = reg
        elif opcode == 1:  # READ
            reg_write_count[('R', reg)] += 1
            last_reg = reg
        else:
            last_reg = reg
    elif ptype == 2:  # Type-2（承接上一个 Type-1 的寄存器，通常是 FDRI）
        pkt_type_count[2] += 1
        opcode = (w >> 27) & 0x3
        wc = w & 0x07FFFFFF
        opcode_count[opcode] += 1
        pos += 4
        if opcode == 2:  # WRITE
            reg = last_reg
            reg_write_count[reg] += 1
            reg_write_words[reg] += wc
            if reg == 2:  # FDRI
                fdri_writes.append((current_far, wc))
            pos += wc * 4
        else:
            pos += wc * 4
    else:
        # 非包字（多为 desync 之后的 NOP/0xFFFF 填充或结尾）
        if w == 0x20000000:
            nop_count += 1
        elif w == 0xFFFFFFFF or w == 0x00000000:
            pass
        else:
            parse_errors += 1
        pos += 4
        # 遇到 DESYNC 之后可能是填充，继续扫描
    # 提前停止：解析错误过多说明已越过配置区
    if parse_errors > 4000:
        break

print("\n=== 配置包类型统计 ===")
print(f"  Type-1 包: {pkt_type_count[1]}")
print(f"  Type-2 包: {pkt_type_count[2]}")
print(f"  NOP 字   : {nop_count}")
print(f"  解析字总数: {words_parsed}  非法/填充异常: {parse_errors}")

print("\n=== 操作码分布 ===")
for op, c in sorted(opcode_count.items()):
    print(f"  {OPC.get(op, op):6s}: {c}")

print("\n=== 寄存器写入统计 (写次数 / 写入字数) ===")
for reg, c in sorted(reg_write_count.items(), key=lambda x: -x[1] if isinstance(x[0], int) else 0):
    if isinstance(reg, tuple):
        name = f"READ:{REG.get(reg[1], reg[1])}"
        print(f"  {name:14s}: {c} 次")
    else:
        name = REG.get(reg, f"reg{reg}")
        print(f"  {name:14s}: {c:5d} 次 / {reg_write_words[reg]:>10d} 字")

print("\n=== CMD 命令序列 ===")
print("  " + " ".join(CMD.get(c, hex(c)) for c in cmd_seq))

def decode_far(v):
    if v is None:
        return "None"
    blk = (v >> 23) & 0x7
    tb = (v >> 22) & 0x1
    row = (v >> 17) & 0x1F
    col = (v >> 7) & 0x3FF
    minor = v & 0x7F
    blkname = {0: "logic(CLB/IO/CLK)", 1: "BRAM内容", 2: "CFG_CLB",
               3: "resv", 4: "resv"}.get(blk, f"blk{blk}")
    return f"blk={blk}({blkname}) T/B={tb} row={row} col={col} minor={minor}"

print("\n=== 关键单字寄存器值 ===")
for reg in (12, 5, 24, 9, 14, 16, 6, 0):
    vals = reg_write_values.get(reg)
    if vals:
        name = REG.get(reg)
        uniq = []
        for v in vals:
            if v not in uniq:
                uniq.append(v)
        print(f"  {name:8s}: " + ", ".join(f"0x{v:08X}" for v in uniq[:6]))

# IDCODE 交叉库
IDCODES = {0x03647093: "XC7K70T", 0x0364C093: "XC7K160T",
           0x03651093: "XC7K325T", 0x03656093: "XC7K410T",
           0x0362C093: "XC7A35T/50T", 0x0362D093: "XC7A100T",
           0x03636093: "XC7A200T"}
idc = reg_write_values.get(12, [])
if idc:
    v = idc[0]
    print(f"\n=== IDCODE 判定 ===\n  IDCODE=0x{v:08X} -> {IDCODES.get(v, '未匹配已知库')}")

# CTL0 加密位
ctl0 = reg_write_values.get(5, [])
if ctl0:
    v = ctl0[0]
    print(f"  CTL0=0x{v:08X}  DEC(bit6)={'1 加密' if v & 0x40 else '0 未加密'}  "
          f"GTS_USR_B(bit0)={v&1}")

# WBSTAR (multiboot 起始地址)
wb = reg_write_values.get(16, [])
if wb:
    print(f"  WBSTAR=0x{wb[0]:08X}  ({'非0->multiboot' if wb[0] else '0->单镜像'})")

# ---------- FAR/FDRI 帧分析 ----------
print("\n=== FAR/FDRI 帧结构 ===")
print(f"  FAR 写入次数: {len(far_writes)}")
print(f"  FDRI 写入次数: {len(fdri_writes)}")
total_fdri_words = sum(wc for _, wc in fdri_writes)
print(f"  FDRI 写入字总数: {total_fdri_words} ({total_fdri_words*4} 字节)")
print(f"  推算配置帧数(=字数/{WORDS_PER_FRAME}): {total_fdri_words/WORDS_PER_FRAME:.1f}")

# 前若干 FAR 值解码
print("\n  前 20 个 FAR 值解码:")
for v in far_writes[:20]:
    print(f"    0x{v:08X}  {decode_far(v)}")

# 按 FDRI 起始 FAR 的块类型统计写入字数（粗估：仅按每段起始 FAR 归类）
blk_words = collections.Counter()
for far, wc in fdri_writes:
    blk = ((far >> 23) & 0x7) if far is not None else -1
    blk_words[blk] += wc
print("\n  FDRI 段按【起始 FAR 块类型】归类的写入字数(粗估):")
blkname = {0: "logic(CLB/IO/CLK)", 1: "BRAM内容", 2: "CFG_CLB", -1: "无FAR"}
for blk, wc in sorted(blk_words.items()):
    print(f"    blk={blk} {blkname.get(blk, ''):20s}: {wc} 字 ({wc/WORDS_PER_FRAME:.1f} 帧)")

# ---------- 熵（判断加密/压缩） ----------
def entropy(buf):
    if not buf:
        return 0.0
    c = collections.Counter(buf)
    n = len(buf)
    return -sum((v/n) * math.log2(v/n) for v in c.values())

body = data[sync_off:sync_off + min(0x200000, len(data)-sync_off)]
print(f"\n=== 熵 ===\n  同步字后 {len(body)} 字节熵: {entropy(body):.4f} bit/byte "
      f"(接近8=加密/压缩; ~1-2=普通未加密配置数据)")

# ---------- 明文字符串扫描：软核/外设线索 ----------
print("\n=== 软核/外设明文特征扫描 ===")
import re
keys = [b"MicroBlaze", b"microblaze", b"PicoBlaze", b"kcpsm", b"KCPSM",
        b"AXI", b"axi_", b"Ethernet", b"ethernet", b"TEMAC", b"tri_mode",
        b"GMII", b"RGMII", b"MDIO", b"MicroBlaze", b"FTDI", b"FT600", b"FT601",
        b"FT245", b"UART", b"IIC", b"I2C", b"SPI", b"MIG", b"DDR3", b"FIFO",
        b"Xilinx", b"vivado", b"Vivado", b"UserID", b"ChipScope", b"ILA",
        b"debug_bridge", b"JTAG", b"aurora", b"PCIe", b"pcie"]
found_any = False
for k in keys:
    cnt = data.count(k)
    if cnt:
        found_any = True
        i = data.find(k)
        print(f"  '{k.decode(errors='replace')}': {cnt} 处 (首现 0x{i:X})")
if not found_any:
    print("  (未命中任何软核/外设明文关键字 —— 综合位流已剥离网表符号，属预期)")

# 广谱可打印字符串（长度>=6），看是否有任何有意义 ASCII
print("\n=== 广谱 ASCII 字符串(长度>=6, 采样前 40 条) ===")
strings = []
for m in re.finditer(rb"[\x20-\x7e]{6,}", data):
    s = m.group().decode("ascii", "ignore")
    strings.append((m.start(), s))
print(f"  可打印串总数(>=6): {len(strings)}")
for off, s in strings[:40]:
    print(f"    0x{off:08X}: {s[:60]}")
