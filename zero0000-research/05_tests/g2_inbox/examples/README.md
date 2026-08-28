# G2 SPI CSV 示例（合成 · 非实测）

| 文件 | 用途 |
|------|------|
| `spi_capture.example.csv` | E2E-min：ADC `0x41=0x80`、DAC CONFIG1=`0x11`、CDCE Reg0 internal |
| `spi_capture.saleae_aliases.example.csv` | 同上，Saleae/PulseView 列名别名 |
| `spi_capture.conserviss_min.example.csv` | Conserviss-min：ADC `4180/5004`、DAC CFG1=`0x21`、CDCE Reg0/2/A |

**禁止**把本目录文件复制成 `../spi_capture.csv` 冒充实测。`ingest_g2_inbox.py` 会忽略 `examples/` 与文件名含 `example` 的 CSV。

本地演练：

```bash
cd zero0000-research
python3 scripts/decode_spi_capture.py --self-test
# 端到端（合成钟+SPI → 提案；输出在 _derived/demo_inbox/；禁止回填 G0）
python3 scripts/ingest_g2_inbox.py --demo
```
