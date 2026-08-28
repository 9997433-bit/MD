# G2 inbox（投放实测数据）

把 Day-1 之后的 **时钟 JSON** 与 **SPI CSV** 放进本目录，然后：

```bash
cd zero0000-research
python3 scripts/ingest_g2_inbox.py
```

脚本会：校验文件 →（若有 CSV）**自动列名映射**译码 → `g2_mode_infer` →（Conserviss 命中则挂 `decode_cdce_profile` 先验）→ 写出 `05_tests/G2_inbox_infer_report.md`、`G2_G0回填提案.md` 与哈希。

端到端合成演练（**禁止**当实测）：

```bash
python3 scripts/ingest_g2_inbox.py --demo
```

## 需要的文件名（任选存在即可跑通子集）

| 文件 | 说明 |
|------|------|
| `g2_clocks.json` | 复制自 `g2_clocks.template.json`，填入**实测** Hz（整数，如 `245760000`）；全 null 不算可用 |
| `spi_capture.csv` | LA 导出（放本目录根下，勿放 `examples/`） |
| `NOTES.md` | 可选：探点说明、仅上电/有主机、SW5 拨位 |

SPI CSV 列名：默认 `SCLK,MOSI,SEN,SDENB,SPI_LE`；也可用 Saleae 风格（`SPI_CLK`/`SDATA`/`ADC_CS`/…）。ingest 默认 `--auto-map`，也可用参数覆盖。

**禁止**把未测的猜测 Hz 填进 JSON，或把 `examples/*.csv` 冒充实测。

合成列名演练见 `examples/README.md`。流程总览：`06_docs/G2_资源门禁_用户动作.md`。
