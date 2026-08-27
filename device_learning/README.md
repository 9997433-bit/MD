# Device Static Analysis Learning Package

位流 + 硬件照片的冻结静态学习包。供学习用，不声称厂商等价。

## 声明

> **目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

## 快速开始

```bash
cd device_learning
make help        # 全部命令
make verify      # 生成账本 + 验收
make test        # 104 项 pytest
make dryrun-all  # 合成 EEPROM + USB 演练
make finalize    # ci + health + closure + bundle
make closure     # 静态阶段关闭摘要
make dryrun-all  # 合成 EEPROM + USB 流水线演练（非实机）
```

## 有实物时

```bash
make intake
make check-captures && make phase-b && make proposals
```

## 目录结构

| 路径 | 用途 |
|------|------|
| `firmware/device.bit` | Xilinx Spartan-3 位流 |
| `hardware/photos/` | 硬件拆解照片（10 张） |
| `catalogs/` | HW/BIT/SIG/USB/REF/ARCH/LEARN/EXP 八层 identifier |
| `manifests/` | 哈希、BOM、帧分析、交接包（43+ JSON） |
| `EvidenceLedger.json` | 主账本 |
| `STATIC_CLOSURE.md` | 静态阶段关闭摘要 |
| `phase_b/captures/` | 实机采集放置目录 |
| `phase_c/logs/` | 实验日志目录 |

## 停止条件

1. 所有 identifier 有 status（无空单元格）
2. 八层 catalog 均存在
3. missing/unknown 已登记（见 `BLOCKED_REPORT.md`）
4. 强制 null 桥 ≥ 8 条且未被破坏
5. 无证据不升级 confirmed
6. 敏感词审计通过（`manifests/sensitive_audit.json`）

## 规模

**237 identifier** · **104 pytest** · 静态阶段 **已关闭冻结**

详见 `STATIC_CLOSURE.md` 与 `manifests/handoff_bundle.json`。
