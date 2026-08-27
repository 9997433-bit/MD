# 学习指南

本包供**静态学习**使用，不声称厂商等价。

## 推荐学习顺序

### 第 1 周（纯静态，无需设备）

1. 读 `README.md`、`STATIC_CLOSURE.md`、`EXECUTION_STATUS.md`
2. 看 `manifests/photo_index.json` + `hardware/photos/` — 硬件印象
3. 读 `manifests/hardware_bom.json` — 组件清单
4. 读 `manifests/bitstream_meta.json` + `frame_summary.json` + `frame_deep.json` — 位流结构
5. 对照 `catalogs/catalog_bit.py` 中 `BIT-*` / `FRM-*` confirmed 项
6. 读 `manifests/system_map.json` — 数据路径
7. 读 `bridge_matrix.json` + `OMISSIONS_AND_REMAINING.md` — 诚实边界
8. 读 `manifests/pending_index.json` — 98 条阻塞项

### 第 2 周（需设备）

1. `make handoff` + `make readiness` — 查看缺什么
2. 按 `phase_b/templates/eeprom_read.md` 读取 EEPROM → `phase_b/captures/eeprom.bin`
3. `make check-captures` → `make phase-b`
4. `make proposals` — 审阅升级建议，手动编辑 `catalogs/*.py`
5. 按 `phase_b/templates/usb_capture.md` 抓包
6. `extract_firmware_slice.py` + Ghidra → `phase_b/analysis/mcu_disasm.txt`

### 第 3 周（验证）

1. `phase_c/templates/experiment_log_template.json` — 记录实验
2. `make phase-c` — 校验日志并同步检查清单
3. 引脚/继电器/正弦输入实验 → 人工升级 REF/SIG 层

## 阶段状态

| 阶段 | 状态 |
|------|------|
| A 静态分析 | **完成并已冻结** (`manifests/static_freeze.json`) |
| B 实机采集 | 脚手架就绪；`make dryrun` 可验证合成流水线（非实机数据） |
| C 实验验证 | 脚手架就绪，见 `phase_c/README.md` |
| D 行为复现 | 未开始 |

## 一键命令

```bash
cd device_learning
make verify          # 生成账本 + 验收
make test            # 97 项 pytest
make closure         # 静态阶段关闭摘要
make intake          # 实机接入分步向导
make bundle          # 导出 handoff_bundle.json
make health          # 包健康检查
make handoff         # 实机交接摘要
make readiness       # 阶段 B 就绪报告
make check-captures  # 采集预检
make dryrun          # 合成流水线演练
make phase-b         # 实机采集后刷新
make proposals       # catalog 升级建议（人工审阅）
make phase-c         # 阶段 C 实验日志
make closure         # 静态关闭摘要
```

## 核心声明

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## LEARN 层

`catalogs/catalog_learn.py` 中有 20 条学习检查项，可在账本中追踪完成度。
