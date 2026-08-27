# 阶段 C 实验日志

每次实验在此目录创建 JSON 文件，命名格式：`EXP-XXX-YYYY-MM-DD.json`

## 模板

```json
{
  "experiment_id": "EXP-006",
  "date": "2026-08-27",
  "setup": "继电器切换 + 信号源",
  "observation": "通道 1 切换后输出断开",
  "conclusion": "confirmed",
  "identifiers_upgraded": ["SIG-002-RELAY-MATRIX"],
  "boundary": "仅对本次观察成立"
}
```

## 结论取值

- `confirmed` — 观察支持假设
- `refuted` — 观察否定假设
- `inconclusive` — 无法判定

完成后运行 `python3 scripts/generate_ledger.py` 刷新账本。
