# G2 SPI CSV 示例（合成 · 非实测）

| 文件 | 用途 |
|------|------|
| `spi_capture.example.csv` | 自检波形：ADC `0x41=0x80`、DAC CONFIG1、CDCE Reg0 |
| `spi_capture.saleae_aliases.example.csv` | 同上，列名为 Saleae/PulseView 风格别名 |

**禁止**把本目录文件复制成 `../spi_capture.csv` 冒充实测。`ingest_g2_inbox.py` 会忽略 `examples/` 与文件名含 `example` 的 CSV。

本地演练：

```bash
cd zero0000-research
python3 scripts/decode_spi_capture.py --self-test
python3 scripts/decode_spi_capture.py \
  05_tests/g2_inbox/examples/spi_capture.saleae_aliases.example.csv --auto-map
```
