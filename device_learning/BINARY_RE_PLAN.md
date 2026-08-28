# 二进制自底向上逆向计划与目标

> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**  
> **主证据**：`phase_b/analysis/fx2_ram_from_enum.bin`（USB 枚举 `0xA0` 灌入的易失 RAM，**不是** `eeprom.bin`）。  
> **Oracle**：`usb_session.pcapng` / `usb_enum.pcapng`（只做校验，不替代固件事实）。

## 总目标

从二进制最底层向上，建立可复现的固件地图，直到能把 **EP01 命令分发** 与 **EP84 数据路径** 锚定到具体地址；语义在无 EEPROM/符号前最高 **`candidate`**。

## 分层计划（必须按序，下层未过不去上层）

| 层 | 名称 | 目标 | 成功标准 | 产物 |
|----|------|------|----------|------|
| **L0** | 字节事实 | 映像完整性、熵、零区、入口字节 | sha256 稳定；`0x0000` 为 `LJMP` | `fx2_ram_scan.json` |
| **L1** | 向量与立即数 | 复位/中断向量候选；MOV DPTR/#imm、LJMP/LCALL 目标表 | 向量表与绝对跳转列表可复现 | `fx2_ram_xrefs.json` |
| **L2** | SFR/XDATA 交叉引用 | 标出对 `0xE6xx`（CPUCS/EPCFG/FIFO 等）的访问点 | 每个关键 SFR 有 ≥1 个代码偏移 | 同上 + 笔记 |
| **L3** | 函数粗分割 | 以 RET/入口聚类切出例程边界 | 主入口 `0x075B` 起调用图草稿 | `fx2_ram_routines.json` |
| **L4** | 命令分发 | 在 EP1 相关路径找到 opcode switch/表 | opcode→handler 地址候选表 | `fx2_cmd_dispatch_hypothesis.json` |
| **L5** | 数据路径 | FIFO→USB IN 循环与打包宽度 | 与 EP84 长度/字对齐假设相容 | `fx2_datapath_hypothesis.json` |
| **L6** | 抓包坐实 | 用 session 时序/常量做 oracle | 命中则升 candidate；打脸则回退 | 更新 `protocol_log` / 账本提案 |
| **L7** | EEPROM 对齐 | 有 `eeprom.bin` 后 diff RAM vs C2 | 标明同构/差异区 | `eeprom` manifests + disasm |

### 进度（脚本自动化）

- L0–L2：✅ `analyze_fx2_ram_image.py` / `analyze_fx2_ram_xrefs.py`
- G0–G1：✅ `analyze_fx2_address_map.py` → `fx2_address_map.json` + `fx2_init_chain.json`
- L3–L5：✅ routines / cmd_dispatch / datapath（假设级；`0x1435` 为 L4∩L5 热点）
- L6：✅ `fx2_oracle_crosscheck.json`（`0x08`→candidate 关联，语义 unknown）
- G4 lite：✅ `phase_b/analysis/mcu_disasm.txt`（关键区域；非完整 Ghidra CFG）
- L7：❌ 缺 `eeprom.bin`
- 笔记：`phase_b/analysis/MCU_NOTES.md`

## 里程碑目标（可验收）

1. **G0 — 地图**：L0–L2 完成，任意人可用脚本复现 xref 报告。  
2. **G1 — 入口**：确认并文档化 reset → `0x075B` 初始化链上的关键 SFR 写入顺序。  
3. **G2 — 命令面**：至少 3 个高频 opcode（`0x01/0x08/0x09`）各有 handler 地址候选 + 抓包旁证。  
4. **G3 — 数据面**：指出至少一条从 XDATA/FIFO 到 EP IN 的代码路径候选。  
5. **G4 — 人工反汇编**：Ghidra 导出 `phase_b/analysis/mcu_disasm.txt`（可与脚本互补）。  
6. **G5 — EEPROM**：物理 dump 后做 L7，决定 RAM 镜像是否完整真源。

## 非目标（本阶段不做）

- 把 opcode 语义升为 `confirmed`（缺符号与可控实验）  
- 声称厂商等价或完整掌握运行行为  
- 用合成 EEPROM 夹具冒充实机固件

## 执行节奏

```text
脚本 L0–L2（自动、可 CI）
    → 人工 Ghidra 标注 L3–L5
    → 抓包 oracle L6
    → （阻塞）eeprom L7
```

仓库命令入口（随脚本落地）：

```bash
cd device_learning
python3 scripts/analyze_fx2_ram_image.py      # L0
python3 scripts/analyze_fx2_ram_xrefs.py       # L1–L2
# 后续：analyze_fx2_ram_routines.py 等
```

## 与采集路线图关系

本计划是 **M6 的前置静态支线**：不替代 `ACQUISITION_ROADMAP.md` 的 M1–M5，但为 M1 命令语义与 M3 打包提供固件侧锚点。
