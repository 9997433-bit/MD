# Device Static Analysis Learning Package

位流 + 硬件照片的冻结静态学习包。供学习用，不声称厂商等价。

## 声明

> **目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

## 快速开始

```bash
cd device_learning
make verify    # 生成账本 + 验收
make test      # 76 项 pytest
make health    # 包健康检查
make handoff   # 实机交接摘要
make dryrun    # 合成流水线演练（非实机数据）
make status    # 一行状态摘要
make ci        # verify + test（同 CI）
```

## 目录结构

| 路径 | 用途 |
|------|------|
| `firmware/device.bit` | Xilinx Spartan-3 位流 |
| `hardware/photos/` | 硬件拆解照片（10 张） |
| `catalogs/` | HW/BIT/SIG/USB/REF/ARCH/LEARN/EXP 八层 identifier |
| `manifests/` | 哈希、BOM、帧分析、交叉对照（25+ JSON） |
| `EvidenceLedger.json` | 主账本 |
| `coverage.json` | 完成度 + 停止条件 |
| `bridge_matrix.json` | 强制 null 桥（10 条） |
| `STATIC_REPORT.md` | 自动摘要 |
| `CONFIRMED_REPORT.md` | 68 条 confirmed 项 |
| `BLOCKED_REPORT.md` | 98 条阻塞项 |
| `IDENTIFIER_INDEX.md` | 237 条 identifier 全表 |
| `HARDWARE_HANDOFF.md` | 实机接入指南 |
| `OMISSIONS_AND_REMAINING.md` | 遗漏登记 |
| `phase_b/` | 实机采集脚手架 |
| `phase_c/` | 实验验证脚手架 |

## 停止条件

1. 所有 identifier 有 status（无空单元格）
2. 八层 catalog 均存在
3. missing/unknown 已登记（见 `BLOCKED_REPORT.md`）
4. 强制 null 桥 ≥ 8 条且未被破坏
5. 无证据不升级 confirmed
6. 敏感词审计通过（`manifests/sensitive_audit.json`）

## 实机下一步

见 `HARDWARE_HANDOFF.md`，采集后运行 `make phase-b`。

## 模型

本项目分析采用 Fable 5 模型。
