# MCU 静态分析笔记（二进制主线）

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**  
> **主证据**：`fx2_ram_from_enum.bin`（USB `0xA0` 易失 RAM，**≠** `eeprom.bin`）  
> **计划**：[`BINARY_RE_PLAN.md`](../BINARY_RE_PLAN.md)

## 已确认的底层事实（L0–L2）

| 项 | 值 | 来源 |
|----|-----|------|
| 映像大小 / SHA-256 | 16384 / `ac346119…3241` | `fx2_ram_scan.json` |
| Reset | `0x0000: LJMP 0x075B` | scan + xrefs |
| 绝对跳转热点 | `0x0393`(40), `0x16b7`(30), `0x0473`(18)… | `fx2_ram_xrefs.json` |
| SFR DPTR 命中 | CPUCS, EP1IN/OUTCFG, EP2CS, EP4CFG/CS, EP6CFG/CS, FIFORESET, IFCONFIG, PINFLAGSAB | xrefs |
| Opcode 立即数站点 | `0x01`,`0x08`,`0x04`（MOV A,# / CJNE） | xrefs |

## L3–L5 脚本结果摘要

- **L3**：约 131 个例程种子；覆盖 `0x075B` 的段为 `0x075B–0x07EA`（143B）。
- **L4×L5 收敛点**：opcode **`0x08`** 的立即数站点主要落在例程 **`0x1435`**；该例程同时是数据面最高分候选（命中 EP6CFG/EP6CS/FIFORESET/EP4*/PINFLAGSAB）。  
  → Ghidra **优先打开 `0x1435`**，验证是否为 start/arm 流 + FIFO 配置合一路径（仍为 hypothesis）。
- **L4**：`0x01` 站点偏向 `0x0473`；`0x09/0x0a/0x0b` 未在 `MOV A,#`/`CJNE A,#` 模式中出现（可能用其它比较形式）。
- **Oracle**：EP84 burst 前 `0x08` 频次最高（`usb_cmd_data_correlation.json`）。

## L3–L5 工作方式

1. `analyze_fx2_ram_routines.py` → 例程粗分割  
2. `analyze_fx2_cmd_dispatch.py` → opcode→owner 例程候选（对照 EP84 时序 oracle）  
3. `analyze_fx2_datapath.py` → EP6/FIFO 相关例程打分  

## Ghidra 优先标注清单

1. `0x075B` 主初始化：跟踪至 EP*CFG / FIFORESET / CPUCS  
2. 热点子程序 `0x0393`、`0x16b7`  
3. **`0x1435`**（opcode `0x08` ∩ 数据面最高分）  
4. `0x0473`（opcode `0x01` 主导 owner）  
5. 其它 `fx2_datapath_hypothesis.json` → `primary_followups_for_ghidra`

Language：`8051:LE:16:default`，基址 `0x0000`。导出：`mcu_disasm.txt`。

## 仍阻塞

- 持久 `eeprom.bin`（L7）  
- 完整 CFG / 间接调用（需人工 Ghidra）  
- 样本打包语义（需已知激励实验）
