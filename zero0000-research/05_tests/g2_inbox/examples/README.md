# G2 SPI / 钟 JSON 示例（合成 · 非实测）

| 文件 | 用途 |
|------|------|
| `spi_capture.example.csv` | E2E-min：ADC `0x41=0x80`、DAC CONFIG1=`0x11`、CDCE Reg0 internal |
| `spi_capture.saleae_aliases.example.csv` | 同上，Saleae/PulseView 列名别名 |
| `spi_capture.conserviss_min.example.csv` | Conserviss-min：ADC `4180/5004`、DAC CFG1=`0x21`、CDCE Reg0/2/A |
| `g2_clocks.planA.example.json` | 计划 A 钟格式样例（245.76 / 491.52） |
| `g2_clocks.planB.example.json` | 计划 B 钟格式样例（双路 245.76） |
| `g2_clocks.planC.example.json` | 计划 C 钟格式样例（ADC 61.44 / DACCLK 245.76） |

**禁止**把本目录文件复制成 `../spi_capture.csv` / `../g2_clocks.json` 冒充实测。`ingest_g2_inbox.py` 会忽略 `examples/` 与文件名含 `example` 的 CSV；`mk_g2_clocks.py` 写入 inbox 根须 `--confirm-measured`。

本地演练：

```bash
cd zero0000-research
python3 scripts/decode_spi_capture.py --self-test
python3 scripts/mk_g2_clocks.py --self-test
# 端到端（合成钟+SPI → 提案；输出在 _derived/demo_inbox/；禁止回填 G0）
python3 scripts/ingest_g2_inbox.py --demo
```
