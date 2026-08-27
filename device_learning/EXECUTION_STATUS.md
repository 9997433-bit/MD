# 执行状态

**执行时间**：2026-08-27  
**模型**：Fable 5  
**结论**：阶段 0 / A 已完成；**目录完整**（128 条 identifier）

## 停止条件检查

| # | 条件 | 结果 |
|---|------|------|
| 1 | 所有 identifier 无空 status | ✅ |
| 2 | HW/BIT/SIG/USB 四层齐全 | ✅ |
| 3 | missing/unknown 已登记 | ✅ |
| 4 | 强制 null 桥 ≥ 8 条 | ✅ |
| 5 | 无冒充厂商状态机 | ✅ |

**声明**：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。

## 产物统计

| 层 | 条目数 | status 分布 |
|----|--------|-------------|
| HW | 32 | confirmed 20, candidate 10, unknown 2 |
| BIT | 50 | confirmed 15, candidate 8, unknown 22, hypothesis 5 |
| SIG | 18 | confirmed 1, candidate 7, unknown 4, hypothesis 6 |
| USB | 28 | missing 9, not_started 10, unknown 7, observed 1, candidate 1 |

## 位流扫描摘要

- 配置数据：130952 字节（0x1FF88）
- 帧字计数：65476
- Type-1 估计：4598 / Type-2 估计：3796
- 熵：4.305 bits/byte

## 产物

- `EvidenceLedger.json` — 完整账本
- `coverage.json` — 状态统计，all_pass=true
- `bridge_matrix.json` — 10 条 null 桥
- `manifests/` — 哈希、位流元数据、BOM(32)、帧扫描、引脚假设(22)
- `tests/` — 15 项 pytest 全部通过

## 仍为 missing/unknown（预期）

- FW 层：8051 固件、EEPROM 镜像
- DRV/PROTO 层：驱动、USB 抓包
- IOB/CLK/MEM 深层：帧级解码未闭合

## 重新生成

```bash
cd device_learning
python3 scripts/generate_ledger.py
python3 -m pytest tests/ -q
```
