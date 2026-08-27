# 学习包导航

## 快速开始

```bash
cd device_learning
make verify    # 生成账本 + 验收
make test      # 59 项 pytest
make status    # 一行状态摘要
```

## 目录地图

| 路径 | 用途 |
|------|------|
| `firmware/device.bit` | Xilinx 位流 |
| `hardware/photos/` | 10 张板卡照片 |
| `catalogs/` | 八层 identifier 目录 |
| `manifests/` | 哈希、BOM、帧分析、系统图（26+ JSON） |
| `EvidenceLedger.json` | 主账本 |
| `coverage.json` | 完成度统计 |
| `bridge_matrix.json` | 强制 null 桥 |
| `ARCHITECTURE.md` | 系统数据路径 mermaid 图 |
| `CONFIRMED_REPORT.md` | 68 条 confirmed 项 |
| `BLOCKED_REPORT.md` | 98 条阻塞项 |
| `BRIDGE_REPORT.md` | 10 条 null 桥策略 |
| `IDENTIFIER_INDEX.md` | 237 条 identifier 全表 |
| `HARDWARE_HANDOFF.md` | 实机接入三步指南 |
| `LEARNING_GUIDE.md` | 三周学习路线 |
| `STATIC_REPORT.md` | 自动摘要 |
| `phase_b/` | 实机采集（EEPROM/抓包） |
| `phase_c/` | 实验验证 |
| `phase_b/fixtures/` | 合成参考（非实机数据） |

## 八层 catalog

`hw` · `bit` · `signal` · `usb` · `ref` · `arch` · `learn` · `exp`

## 声明

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 实机下一步

```bash
# 放置采集文件后
make phase-b
```

详见 `HARDWARE_HANDOFF.md`。
