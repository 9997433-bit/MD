# 静态分析报告（自动生成）

**生成时间**：2026-08-28 12:53 UTC

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 摘要

- Identifier 总数：**237**
- 停止条件：**全部通过**
- 阶段：**static_complete_pending_hardware**

### Status 分布

| Status | 数量 |
|--------|------|
| candidate | 80 |
| confirmed | 76 |
| hypothesis | 6 |
| missing | 8 |
| not_started | 19 |
| unknown | 48 |

## 硬件

- 板卡版本：198755F-01L
- BOM 组件：40 条
- 照片索引：10 张

## 位流

- IDCODE：`0x01414093`
- 帧长 FLR：52 words
- FDRI 字数：32648
- 帧估计：627
- IOB candidate 配置字：223
- 位流字符串（脱敏）：367 条
- 配置段熵：4.3049 bits/byte（零字节比 0.5022）

## BOM 交叉对照

- 已链接组件：**27** / 40

## 待解项

- 阻塞 identifier：**75** 条（见 `manifests/pending_index.json`）

## 数据路径

- `NODE-IN` → `NODE-RELAY` (candidate)
- `NODE-RELAY` → `NODE-ADC` (candidate)
- `NODE-ADC` → `NODE-FPGA` (hypothesis)
- `NODE-FPGA` → `NODE-USB-CTL` (hypothesis)
- `NODE-USB-CTL` → `NODE-HOST` (not_started)

## 阶段 B 状态

- EEPROM 已采集：否
- USB 抓包已采集：否

## 阻塞项（需实机）

- EEPROM 转储 → `phase_b/captures/eeprom.bin`
- USB 抓包 → `phase_b/captures/*.pcapng`
- 实验验证 → 见 `phase_c/README.md`
- 接入指南 → `HARDWARE_HANDOFF.md`
- 阶段路线图 → `manifests/phase_roadmap.json`
- 架构图 → `ARCHITECTURE.md`
- Null 桥 → `BRIDGE_REPORT.md`

## 重新生成

```bash
python3 scripts/generate_ledger.py
python3 scripts/build_learning_report.py
```

