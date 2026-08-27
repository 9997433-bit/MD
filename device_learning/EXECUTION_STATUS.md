# 执行状态

**执行时间**：2026-08-27  
**模型**：Fable 5  
**阶段**：A 完成 + B 脚手架就绪  
**结论**：**162 条 identifier**，停止条件 6/6 pass

## 停止条件

| # | 条件 | 结果 |
|---|------|------|
| 1 | 无空 status | ✅ |
| 2 | HW/BIT/SIG/USB/REF 五层齐全 | ✅ |
| 3 | 遗漏已登记 | ✅ |
| 4 | null 桥 ≥ 8 | ✅ |
| 5 | 无冒充厂商等价 | ✅ |
| 6 | 阶段 B 脚手架存在 | ✅ |

## 层统计

| 层 | 条目 | 说明 |
|----|------|------|
| HW | 32 | 硬件 BOM |
| BIT | 60 | 位流 + 深层帧扫描 |
| SIG | 18 | 信号路径 |
| USB | 28 | FW/DRV/PROTO |
| REF | 24 | 公开参考设计信号 |
| **合计** | **162** | |

## 位流深层扫描（新增）

- IDCODE: `0x01414093` (Spartan-3 xc3s200)
- 估计帧数: 627
- candidate IOB 配置字: 223
- Type-1: 4598 / Type-2: 3796 / zero ratio: 39.65%

## 阶段 B 脚手架

- `phase_b/README.md` + 模板（EEPROM/USB/协议记录）
- `scripts/ingest_phase_b.py` — 等待 `captures/` 填入实机数据

## 测试

```bash
cd device_learning && python3 scripts/generate_ledger.py && python3 -m pytest tests/ -q
```

**19 passed**

## 待实机（阶段 B）

- EEPROM 转储 → 升级 FW 层
- USB 抓包 → 升级 PROTO 层
- 引脚对照实验 → 升级 REF/BRG 层
