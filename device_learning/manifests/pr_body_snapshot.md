## 摘要

`device_learning` 位流 + 硬件照片静态学习包，对标 E1733A 账本方法论。

**声明**：目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 规模

| 指标 | 值 |
|------|-----|
| Identifier | **237** |
| pytest | **113** 全部通过 |
| confirmed | 76 |
| blocked | 75 |
| 静态阶段 | **已关闭冻结** (`static_phase_closed.json`) |

## 八层 catalog

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

## 关键能力

- Spartan-3 XC3S200 位流解析（`frame_deep.json`，FRM-011..020）
- `EvidenceLedger.json` + 停止条件验收 + 敏感词审计
- 阶段 B/C 脚手架：`make intake` · `make phase-b` · `make phase-c`
- 合成 EEPROM 夹具检测（不误标 `observed`）
- `manifests/handoff_bundle.json` 一站式交接包

## 验证

```bash
cd device_learning
make ci && make health && make closure
```

## 阻塞（需实机）

- `phase_b/captures/eeprom.bin` (8192 B)
- `phase_b/captures/*.pcapng`

## 有实物时

```bash
make intake
make check-captures && make phase-b && make proposals
```
