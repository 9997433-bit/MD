#!/usr/bin/env python3
"""
MCS / Intel-HEX 固件结构分析脚本
用途：解析 Intel HEX 记录、重建线性镜像、定位 Xilinx 7-series 比特流特征字。
"""
import sys
import collections

PATH = "/tmp/zero0000/20230825_s2056.mcs"

# ---------- 1. 解析 Intel HEX ----------
rec_types = collections.Counter()
data_bytes_total = 0
ela_upper = 0          # 扩展线性地址高 16 位
segments = {}          # base_upper -> [(addr32, bytes)]
min_addr = None
max_addr = None
first_data_addr = None
image = bytearray()    # 简化：按 32 位地址稀疏重建
addr_map = {}          # abs_addr -> byte  (对本例连续，直接用 bytearray 更省内存)

# 因为镜像可能很大且基本连续，采用 dict 记录段起点，最后拼接
flat = bytearray()
expected_next = None
gaps = []

with open(PATH, "r") as f:
    for lineno, line in enumerate(f, 1):
        line = line.strip()
        if not line or line[0] != ":":
            continue
        bytecount = int(line[1:3], 16)
        offset = int(line[3:7], 16)
        rtype = int(line[7:9], 16)
        data = bytes.fromhex(line[9:9 + bytecount * 2])
        # 校验和
        raw = bytes.fromhex(line[1:9 + bytecount * 2 + 2])
        if (sum(raw) & 0xFF) != 0:
            print(f"[WARN] 行 {lineno} 校验和错误")
        rec_types[rtype] += 1
        if rtype == 0x00:            # 数据
            data_bytes_total += bytecount
            abs_addr = (ela_upper << 16) | offset
            if first_data_addr is None:
                first_data_addr = abs_addr
            if min_addr is None or abs_addr < min_addr:
                min_addr = abs_addr
            end = abs_addr + bytecount
            if max_addr is None or end > max_addr:
                max_addr = end
            if expected_next is not None and abs_addr != expected_next:
                gaps.append((expected_next, abs_addr))
            flat.extend(data)
            expected_next = end
        elif rtype == 0x04:          # 扩展线性地址
            ela_upper = int.from_bytes(data, "big")
        elif rtype == 0x02:          # 扩展段地址
            pass
        elif rtype == 0x01:          # EOF
            pass

print("=== Intel HEX 记录统计 ===")
names = {0x00: "00 数据", 0x01: "01 EOF", 0x02: "02 扩展段地址",
         0x03: "03 起始段地址", 0x04: "04 扩展线性地址", 0x05: "05 起始线性地址"}
for t, c in sorted(rec_types.items()):
    print(f"  {names.get(t, hex(t)):20s}: {c}")
print(f"数据字节总量: {data_bytes_total} (0x{data_bytes_total:X}) = {data_bytes_total/1024/1024:.3f} MiB")
print(f"地址范围: 0x{min_addr:08X} .. 0x{max_addr:08X}")
print(f"重建连续镜像长度: {len(flat)} 字节")
print(f"地址间隙数: {len(gaps)}")
for g in gaps[:10]:
    print(f"   gap: 0x{g[0]:08X} -> 0x{g[1]:08X}")

# ---------- 2/3. 特征字搜索 ----------
def find_all(buf, pat):
    out = []
    start = 0
    while True:
        i = buf.find(pat, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out

patterns = {
    "同步字 AA995566": bytes.fromhex("AA995566"),
    "同步字(位反) 995566AA": bytes.fromhex("995566AA"),
    "boot header BB11220044": bytes.fromhex("BB11220044"),
    "总线宽度检测 000000BB": bytes.fromhex("000000BB"),
    "dummy pad FFFFFFFF*4": bytes.fromhex("FFFFFFFF" * 4),
}
print("\n=== 特征字搜索 (在重建镜像中的偏移) ===")
for name, pat in patterns.items():
    hits = find_all(flat, pat)
    show = ", ".join(f"0x{h:X}" for h in hits[:8])
    print(f"  {name:26s}: {len(hits):6d} 处  {show}")

# IDCODE：紧随 sync 之后的比特流命令流里，格式 30018001 <IDCODE32> (Type1 write to IDCODE reg 0x0C)
# 7-series 常见 IDCODE
idcodes = {
    "XC7K160T": 0x03631093, "XC7K325T": 0x03651093, "XC7K410T": 0x03656093,
    "XC7A100T": 0x0362D093, "XC7A200T": 0x03636093, "XC7A35T": 0x0362C093,
    "XC7A50T": 0x0362C093, "XC7A75T": 0x0362F093, "XC7Z020": 0x03727093,
    "XC7K70T": 0x03647093, "XC7VX330T": 0x03667093,
}
print("\n=== 7-series IDCODE 扫描 ===")
# 写 IDCODE 寄存器的 Type-1 命令: 0x30018001
cmd = bytes.fromhex("30018001")
for off in find_all(flat, cmd):
    val = int.from_bytes(flat[off + 4:off + 8], "big")
    match = [k for k, v in idcodes.items() if v == val]
    print(f"  @0x{off:X}  IDCODE=0x{val:08X}  {match if match else '(未知/未匹配已知库)'}")
# 也直接扫描 IDCODE 值本身
for name, code in idcodes.items():
    hits = find_all(flat, code.to_bytes(4, "big"))
    if hits:
        print(f"  直接匹配 {name}=0x{code:08X}: {len(hits)} 处 @ {[hex(h) for h in hits[:4]]}")

# ---------- 5. 明文 Xilinx 字符串 / 加密判断 ----------
print("\n=== 明文字符串 / 加密线索 ===")
for s in [b"Xilinx", b"vivado", b"Vivado", b".ncd", b".bit", b"UserID",
          b"7k160", b"xc7k", b"HMAC", b"; Xilinx"]:
    hits = find_all(flat, s)
    if hits:
        sd = s.decode(errors="replace")
        print(f"  '{sd}': {len(hits)} 处 @ {[hex(h) for h in hits[:4]]}")

# 熵估计（在 sync 之后一段，判断是否加密）
def entropy(buf):
    if not buf:
        return 0.0
    c = collections.Counter(buf)
    import math
    n = len(buf)
    return -sum((v/n) * math.log2(v/n) for v in c.values())

sync_hits = find_all(flat, bytes.fromhex("AA995566"))
if sync_hits:
    s0 = sync_hits[0]
    body = flat[s0:s0 + 0x100000]
    print(f"  首个 sync 后 1MiB 熵: {entropy(body):.4f} bits/byte (>7.9 强烈提示加密/压缩)")

# 加密标志：写 CTL0 寄存器打开 DEC bit。命令 30008001 <CTL0>；DEC=bit6(0x40)
ctl = bytes.fromhex("30008001")
print("\n=== CTL0 (加密 DEC 位) 检查 ===")
for off in find_all(flat, ctl)[:6]:
    val = int.from_bytes(flat[off + 4:off + 8], "big")
    dec = "DEC=1(加密)" if val & 0x40 else "DEC=0(未加密)"
    print(f"  @0x{off:X}  CTL0=0x{val:08X}  {dec}")

# ---------- 4. Flash 占用 / 镜像数量 ----------
print("\n=== Flash 占用估计 ===")
print(f"  地址跨度: {max_addr-min_addr} 字节 ({(max_addr-min_addr)/1024/1024:.2f} MiB)")
print(f"  实际数据: {data_bytes_total} 字节 ({data_bytes_total/1024/1024:.2f} MiB)")
print(f"  sync 字出现次数(=候选比特流/镜像数): {len(sync_hits)}")
