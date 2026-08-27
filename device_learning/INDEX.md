# 学习包导航

## 快速开始

```bash
cd device_learning
make verify       # 生成账本 + 验收
make test         # 94 项 pytest
make health       # 包健康检查
make handoff      # 实机交接摘要
make readiness    # 阶段 B 就绪报告
make check-captures  # 采集预检
make phase-b      # 实机采集后刷新
make phase-c      # 实验日志处理
make proposals    # 查看升级建议
make status       # 一行状态摘要
```

## 目录地图

| 路径 | 用途 |
|------|------|
| `firmware/device.bit` | Xilinx 位流 |
| `hardware/photos/` | 10 张板卡照片 |
| `catalogs/` | 八层 identifier 目录 |
| `manifests/` | 哈希、BOM、帧分析、系统图（35+ JSON） |
| `EvidenceLedger.json` | 主账本 |
| `coverage.json` | 完成度统计 |
| `bridge_matrix.json` | 强制 null 桥 |
| `PHASE_B_READINESS.md` | 阶段 B 阻塞项 |
| `PHASE_C_READINESS.md` | 阶段 C 前置与进度 |
| `HARDWARE_HANDOFF.md` | 实机接入三步指南 |
| `manifests/phase_b_upgrade_proposals.json` | catalog 升级建议（人工审阅） |
| `phase_b/captures/` | 实机采集放置目录 |
| `phase_c/logs/` | 实验日志目录 |

## 八层 catalog

`hw` · `bit` · `signal` · `usb` · `ref` · `arch` · `learn` · `exp` — **237 条 identifier**

## 声明

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 实机下一步

1. 阅读 `HARDWARE_HANDOFF.md`
2. 放置 `phase_b/captures/eeprom.bin` 与 `*.pcapng`
3. `make check-captures && make phase-b`
4. `make proposals` 审阅升级建议后手动编辑 `catalogs/*.py`
