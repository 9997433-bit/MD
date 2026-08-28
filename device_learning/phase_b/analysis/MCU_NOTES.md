# MCU 静态分析笔记（二进制主线）

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**  
> **主证据**：`fx2_ram_from_enum.bin`（USB `0xA0` 易失 RAM，**≠** `eeprom.bin`）  
> **计划**：[`BINARY_RE_PLAN.md`](../BINARY_RE_PLAN.md)

## 已确认的底层事实（L0–L2 / G0–G1）

| 项 | 值 | 来源 |
|----|-----|------|
| 映像大小 / SHA-256 | 16384 / `ac346119…3241` | `fx2_ram_scan.json` |
| Reset | `0x0000: LJMP 0x075B` | scan + xrefs + `fx2_ivt_map.json` |
| 地址图 | 16KiB code 映像 + IVT + SFR/XDATA 引用窗 | `fx2_address_map.json` |
| Init SFR 首见写序 | `SUDPTRH` → … → `EP4BC*` → `EP8BCL`/`EP6BCL` → `I2CS`/`I2DAT` → `EP6FIFOCFG` → `PINFLAGS*`（candidate） | `fx2_init_chain.json` |
| CRT / early hub | `0x075B` 清 IRAM → `LJMP 0x07A5`；early `LCALL/LJMP 0x1435` | 同上 |
| 绝对跳转热点 | `0x0393`(40), `0x16b7`(30), `0x0473`(18)… | `fx2_ram_xrefs.json` |
| SFR DPTR 命中 | CPUCS, EP1IN/OUTCFG, EP2CS, EP4CFG/CS, EP6CFG/CS, FIFORESET, IFCONFIG, PINFLAGSAB | xrefs |
| Opcode 立即数站点 | `0x01`,`0x08`,`0x09`,`0x0a`,`0x04`,`0x05` | xrefs / dispatch |

## L3–L5 脚本结果摘要

- **L3**：约 131 个例程种子；覆盖 `0x075B` 的段为 `0x075B–0x07EA`（143B）。
- **L4×L5 收敛点**：opcode **`0x08`** 的立即数站点主要落在例程 **`0x1435`**；该例程同时是数据面最高分候选（命中 EP6CFG/EP6CS/FIFORESET/EP4*/PINFLAGSAB）。  
  → Ghidra **优先打开 `0x1435`**，验证是否为 start/arm 流 + FIFO 配置合一路径（仍为 hypothesis→candidate 关联）。
- **L4 高频 opcode 候选 owner（G2）**：
  - `0x01` → `0x054c` / `0x0473`（oracle EP84-precede 强）
  - `0x08` → **`0x1435`**（与数据面重叠 + oracle 最强）
  - `0x09` → `0x1c5b`（站点稀疏，仍为 candidate）
- **Oracle**：EP84 burst 前 `0x08` 频次最高（`usb_cmd_data_correlation.json`）。

## L3–L5 工作方式

1. `analyze_fx2_ram_routines.py` → 例程粗分割  
2. `analyze_fx2_cmd_dispatch.py` → opcode→owner 例程候选（对照 EP84 时序 oracle）  
3. `analyze_fx2_datapath.py` → EP6/FIFO 相关例程打分  
4. `analyze_fx2_address_map.py` → 地址图 + `0x075B` init SFR 序  

## IVT / 0x1435

- 中断向量图：`manifests/fx2_ivt_map.json`（reset→`0x075B`，IE0→`0x0F2A`，TF0→`0x1F64`，TF1→`0x30B3`，`0x0043`→`0x1B00`）
- `0x1435` 注解：`manifests/fx2_routine_1435_annotation.json`  
  - 窗口内反复 `MOV DPTR,#EP6CS/EP4CS`  
  - 同窗 `MOV A,#0x08`（两处）与 `MOV A,#0x04`

## G4 lite disasm

- 文本：`phase_b/analysis/mcu_disasm.txt`（关键区域，非完整 Ghidra）
- 索引：`manifests/fx2_ram_disasm.json`
- L6 交叉：`manifests/fx2_oracle_crosscheck.json`（`0x08`∩`0x1435`∩EP84 oracle → candidate 级关联，语义仍 unknown）

## Ghidra 优先标注清单

1. `0x075B` 主初始化：对照 `fx2_init_chain.json` 的 SFR 首见写序  
2. 热点子程序 `0x0393`、`0x16b7`  
3. **`0x1435`**（opcode `0x08` ∩ 数据面最高分）  
4. `0x0473` / `0x054c`（opcode `0x01`）  
5. `0x1c5b`（opcode `0x09`）  
6. 其它 `fx2_datapath_hypothesis.json` → `primary_followups_for_ghidra`

Language：`8051:LE:16:default`，基址 `0x0000`。导出：`mcu_disasm.txt`。

## 仍阻塞

- 持久 `eeprom.bin`（L7）  
- 完整 CFG / 间接调用（需人工 Ghidra）  
- 样本打包语义（需已知激励实验）  
- opcode **语义**升 `confirmed`（本阶段禁止；最高 `candidate`）
