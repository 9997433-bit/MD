# 学习包导航

## 快速开始

```bash
cd device_learning
make verify         # 生成账本 + 验收
make test           # 100 项 pytest
make help           # 命令列表
make health         # 包健康检查
make closure        # 静态阶段关闭摘要
make intake         # 实机接入分步向导（有实物时入口）
make handoff        # 实机交接摘要
make bundle         # handoff_bundle.json + pr_body_snapshot.md
make resume         # Agent 恢复 JSON
make finalize       # 全量收尾验收
make readiness      # 阶段 B 就绪报告
make check-captures # 采集预检
make phase-b        # 实机采集后刷新
make proposals      # catalog 升级建议
make phase-c        # 实验日志处理
make status         # 一行状态摘要
```

## 目录地图

| 路径 | 用途 |
|------|------|
| `STATIC_CLOSURE.md` | 静态阶段关闭摘要 |
| `firmware/device.bit` | Xilinx 位流 |
| `hardware/photos/` | 10 张板卡照片 |
| `catalogs/` | 八层 identifier 目录 |
| `manifests/handoff_bundle.json` | 实机恢复用一站式 JSON |
| `EvidenceLedger.json` | 主账本 |
| `PHASE_B_READINESS.md` / `PHASE_C_READINESS.md` | 阶段就绪报告 |
| `HARDWARE_HANDOFF.md` | 实机接入指南 |
| `phase_b/captures/` | 采集物放置目录 |

## 八层 catalog

**237 条 identifier** — `hw` · `bit` · `signal` · `usb` · `ref` · `arch` · `learn` · `exp`

## 声明

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 有实物时

```bash
make intake
make check-captures && make phase-b && make proposals
```
