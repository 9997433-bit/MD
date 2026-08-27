# 执行状态

**阶段**：A 深化 + B 脚手架 + 学习索引  
**规模**：**221 条 identifier**，**31 pytest**，停止条件 **8/8 pass**

## 层统计

| 层 | 条目 |
|----|------|
| HW | 32 |
| BIT | 78 |
| SIG | 19 |
| USB | 33 |
| REF | 24 |
| ARCH | 15 |
| LEARN | 20 |
| **合计** | **221** |

## 本轮新增

- `LEARNING_GUIDE.md` — 三周学习路线
- `catalog_learn.py` — 20 条学习检查项
- `manifests/photo_index.json` — 10 张照片 × 75 组件引用
- `manifests/crossref_index.json` — 跨层主题索引
- `scripts/redact_manifests.py` — 敏感词脱敏
- `scripts/scan_firmware_stub.py` — 8051 分析占位

## 帧深层（更新）

- FAR 直写 1 次，逻辑列估计 33
- Type-1 包 72 / Type-2 包 1
- 寄存器写入：CMD×7, FLR, COR, IDCODE, FAR, CRC

## 生成

```bash
cd device_learning && python3 scripts/generate_ledger.py && python3 -m pytest tests/ -q
```

## 阻塞（需实机）

EEPROM / USB 抓包 → `phase_b/captures/`
