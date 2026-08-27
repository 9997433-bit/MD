# 阶段 C：实验验证

在阶段 B 采集到 EEPROM / 抓包数据后，用下列实验把 `hypothesis` / `candidate` 升级为 `confirmed` 或打回 `refuted`。

## 实验清单

| ID | 实验 | 依赖 | 升级目标 |
|----|------|------|----------|
| EXP-004 | Slave FIFO 引脚探测 | 示波器 | BRG-001..009, REF-USB-* |
| EXP-005 | ADC 时序探测 | 示波器 | REF-ADC-*, IOB-006 |
| EXP-006 | 继电器切换 | 信号源 | SIG-002, ARCH-013 |
| EXP-007 | AC/DC 耦合 | 驱动或手动 | SIG-006 |
| EXP-008 | 已知正弦输入 | AWG + 驱动 | SIG-007, SIG-018 |
| EXP-009 | IFCLK 频率测量 | 频率计 | REF-IFCLK, ARCH-006 |
| EXP-010 | 8051 反汇编 | EXP-001 | FW-MCU-* |
| EXP-011 | 协议命令表 | EXP-003 | PROTO-* |
| EXP-014 | 数据帧格式 | EXP-008 | SIG-018-DATA-PACK |

## 记录模板

复制 `phase_c/templates/experiment_log_template.json` 到 `phase_c/logs/EXP-XXX-YYYYMMDD.json`。

每次实验在 `phase_c/logs/` 创建：

```json
{
  "experiment_id": "EXP-006",
  "date": "YYYY-MM-DD",
  "setup": "...",
  "observation": "...",
  "conclusion": "confirmed|refuted|inconclusive",
  "identifiers_upgraded": ["SIG-002-RELAY-MATRIX"]
}
```

## 诚实边界

- 单次实验不足以声称完整协议理解
- `confirmed` 仅对本次观察范围内成立
