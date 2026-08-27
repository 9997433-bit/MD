# Device Static Analysis Learning Package

位流 + 硬件照片的冻结静态学习包。供学习用，不声称厂商等价。

## 声明

> **目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

## 生成

```bash
cd device_learning
python3 scripts/generate_ledger.py
python3 -m pytest tests/ -q
```

## 目录结构

| 路径 | 用途 |
|------|------|
| `firmware/device.bit` | Xilinx Spartan-3 位流 |
| `hardware/photos/` | 硬件拆解照片 |
| `manifests/` | 哈希、元数据、BOM、引脚假设 |
| `catalogs/` | HW/BIT/SIG/USB 四层 identifier |
| `EvidenceLedger.json` | 主账本 |
| `coverage.json` | 完成度 + 停止条件 |
| `bridge_matrix.json` | 强制 null 桥 |
| `OMISSIONS_AND_REMAINING.md` | 遗漏登记 |

## 停止条件

1. 所有 identifier 有 status（无空单元格）
2. HW/BIT/SIG/USB 四层均存在
3. missing/unknown 已登记
4. 强制 null 桥 ≥ 8 条且未被破坏
5. 无证据不升级 confirmed

## 模型

本项目分析采用 Fable 5 模型。
