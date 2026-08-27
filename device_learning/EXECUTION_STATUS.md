# 执行状态

**阶段**：静态分析 **完成**（等待实机）  
**规模**：**237 条 identifier**，**99 pytest**，静态阶段 **已关闭并冻结**

## 八层目录

| 层 | 条目 |
|----|------|
| HW | 32 |
| BIT | 78 |
| SIG | 19 |
| USB | 34 |
| REF | 24 |
| ARCH | 15 |
| LEARN | 20 |
| EXP | 15 |
| **合计** | **237** |

## 静态阶段验收

```bash
make verify
# 或
python3 scripts/verify_completion.py
# → static_phase_complete: true
```

## 关键产物

| 文件 | 用途 |
|------|------|
| `STATIC_REPORT.md` | 人类可读摘要 |
| `IDENTIFIER_INDEX.md` | 237 条 identifier 全表 |
| `manifests/evidence_summary.json` | 一页式证据摘要 |
| `manifests/catalog_integrity.json` | 目录 schema 校验 |
| `CONFIRMED_REPORT.md` | 68 条 confirmed 项 |
| `BLOCKED_REPORT.md` | 98 条阻塞项人类可读表 |
| `ARCHITECTURE.md` | 系统数据路径 mermaid 图 |
| `BRIDGE_REPORT.md` | 10 条 null 桥策略 |
| `manifests/static_phase_closed.json` | 静态阶段关闭标记 |
| `manifests/static_freeze.json` | 冻结快照 |
| `manifests/output_hashes.json` | 产物 SHA256 清单 |
| `phase_b/CHECKLIST.json` | 阶段 B 机器可读检查清单 |
| `manifests/pending_index.json` | 98 条阻塞项 |
| `manifests/phase_roadmap.json` | 阶段 B/C 解锁路线 |
| `HARDWARE_HANDOFF.md` | 实机接入步骤 |
| `STATIC_CLOSURE.md` | 静态阶段关闭摘要 |
| `PHASE_B_READINESS.md` | 阶段 B 阻塞项与就绪状态 |
| `manifests/handoff_bundle.json` | 实机恢复一站式 JSON 包 |
| `manifests/phase_b_upgrade_proposals.json` | 采集后 catalog 升级建议（需人工审阅） |

## 一键命令

```bash
make ledger    # 生成账本
make test      # 运行测试
make closure   # 静态关闭摘要
make intake    # 实机接入分步向导
make handoff   # 实机交接摘要
make readiness # 阶段 B 就绪报告
make check-captures  # 采集文件预检
make bundle    # 导出 handoff_bundle.json
make phase-b   # 实机采集后刷新
make phase-c   # 实验日志校验
```

## 下一步（需实物）

1. 阅读 `HARDWARE_HANDOFF.md`
2. `phase_b/captures/eeprom.bin`
3. `phase_b/captures/*.pcapng`
4. 按 `phase_c/README.md` 做实验验证
