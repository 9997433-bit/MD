# 静态分析报告（自动生成）

**生成时间**：2026-08-27 15:26 UTC

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 摘要

- Identifier 总数：**236**
- 停止条件：**全部通过**
- 阶段：**static_complete_pending_hardware**

### Status 分布

| Status | 数量 |
|--------|------|
| candidate | 64 |
| confirmed | 68 |
| hypothesis | 6 |
| missing | 12 |
| not_started | 30 |
| unknown | 56 |

## 硬件

- BOM 组件：40 条
- 照片索引：10 张

## 位流

- IDCODE：`0x01414093`
- 帧长 FLR：52 words
- FDRI 字数：32648
- 帧估计：627
- IOB candidate 配置字：223

## 数据路径

- `NODE-IN` → `NODE-RELAY` (candidate)
- `NODE-RELAY` → `NODE-ADC` (candidate)
- `NODE-ADC` → `NODE-FPGA` (hypothesis)
- `NODE-FPGA` → `NODE-USB-CTL` (hypothesis)
- `NODE-USB-CTL` → `NODE-HOST` (not_started)

## 阻塞项（需实机）

- EEPROM 转储 → `phase_b/captures/eeprom.bin`
- USB 抓包 → `phase_b/captures/*.pcapng`
- 实验验证 → 见 `phase_c/README.md`

## 重新生成

```bash
python3 scripts/generate_ledger.py
python3 scripts/build_learning_report.py
```

