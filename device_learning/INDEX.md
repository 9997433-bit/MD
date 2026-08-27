# 学习包导航

## 快速开始

```bash
cd device_learning
python3 scripts/generate_ledger.py
python3 scripts/verify_completion.py
python3 -m pytest tests/ -q
cat STATIC_REPORT.md
```

## 目录地图

| 路径 | 用途 |
|------|------|
| `firmware/device.bit` | Xilinx 位流 |
| `hardware/photos/` | 10 张板卡照片 |
| `catalogs/` | 八层 identifier 目录 |
| `manifests/` | 哈希、BOM、帧分析、系统图 |
| `EvidenceLedger.json` | 主账本 |
| `coverage.json` | 完成度统计 |
| `bridge_matrix.json` | 强制 null 桥 |
| `LEARNING_GUIDE.md` | 三周学习路线 |
| `HARDWARE_HANDOFF.md` | 实机接入三步指南 |
| `STATIC_REPORT.md` | 自动摘要 |
| `manifests/pending_index.json` | 阻塞 identifier 索引 |
| `IDENTIFIER_INDEX.md` | 237 条 identifier 全表 |
| `manifests/bom_crosswalk.json` | BOM → HW 交叉对照 |
| `phase_b/` | 实机采集（EEPROM/抓包） |
| `phase_c/` | 实验验证 |
| `phase_b/fixtures/` | 合成参考（非实机数据） |

## 八层 catalog

`hw` · `bit` · `signal` · `usb` · `ref` · `arch` · `learn` · `exp`

## 声明

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 实机下一步

阅读 `HARDWARE_HANDOFF.md`，然后：

1. 放 `eeprom.bin` → `phase_b/captures/`
2. 放 `*.pcapng` → `phase_b/captures/`
3. 运行 `python3 scripts/run_phase_b.py`

无实机时可运行合成夹具测试流水线：

```bash
python3 scripts/build_eeprom_synthetic.py
python3 scripts/analyze_eeprom.py
```
