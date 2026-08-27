# 学习指南

本包供**静态学习**使用，不声称厂商等价。

## 推荐学习顺序

### 第 1 周（纯静态，无需设备）

1. 读 `README.md` 与 `EXECUTION_STATUS.md` — 了解停止条件
2. 看 `manifests/photo_index.json` + `hardware/photos/` — 建立硬件印象
3. 读 `manifests/hardware_bom.json` — 32+ 组件清单
4. 读 `manifests/bitstream_meta.json` + `frame_summary.json` — 位流结构
5. 对照 `catalogs/catalog_bit.py` 中 `BIT-*` confirmed 项
6. 读 `manifests/system_map.json` — 数据路径
7. 读 `catalogs/catalog_ref.py` — 公开参考信号（candidate）
8. 读 `bridge_matrix.json` + `OMISSIONS_AND_REMAINING.md` — 诚实边界

### 第 2 周（需设备）

1. 按 `phase_b/templates/eeprom_read.md` 读取 EEPROM
2. 运行 `python3 scripts/analyze_eeprom.py` + `scan_firmware_stub.py`
3. 按 `phase_b/templates/usb_capture.md` 抓包
4. 填写 `protocol_log_template.json`
5. 运行 `python3 scripts/ingest_phase_b.py` + `generate_ledger.py`

### 第 3 周（验证）

1. 引脚对照实验 → 升级 REF/BRG 层 status
2. 继电器切换实验 → 验证 SIG-002
3. 正弦输入 + 抓包 → 验证数据帧格式

## 阶段状态

| 阶段 | 状态 |
|------|------|
| A 静态分析 | **完成** (`verify_completion.py` → `static_phase_complete: true`) |
| B 实机采集 | 脚手架就绪，等待 `phase_b/captures/` |
| C 实验验证 | 脚手架就绪，见 `phase_c/README.md` |
| D 行为复现 | 未开始 |

## 一键命令

```bash
cd device_learning
python3 scripts/generate_ledger.py   # 生成账本 + STATIC_REPORT.md
python3 scripts/verify_completion.py # 静态阶段验收
python3 -m pytest tests/ -q          # 35 项测试
```

## 核心声明

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## LEARN 层

`catalogs/catalog_learn.py` 中有 20 条学习检查项，可在账本中追踪完成度。
