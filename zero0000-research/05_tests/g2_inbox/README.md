# G2 inbox（投放实测数据）

把 Day-1 之后的 **时钟 JSON** 与 **SPI CSV** 放进本目录，然后：

```bash
cd zero0000-research
python3 scripts/ingest_g2_inbox.py
```

脚本会：校验文件 →（若有 CSV）译码 → `g2_mode_infer` → 写出 `05_tests/G2_inbox_infer_report.md` 与哈希。

## 需要的文件名（任选存在即可跑通子集）

| 文件 | 说明 |
|------|------|
| `g2_clocks.json` | 复制自 `g2_clocks.template.json`，填入实测 Hz（整数，如 `245760000`） |
| `spi_capture.csv` | LA 导出；列名可用默认或见下方 |
| `NOTES.md` | 可选：探点照片说明、仅上电/有主机、SW5 拨位 |

SPI CSV 列名默认：`SCLK,MOSI,SEN,SDENB,SPI_LE`（可用 `ingest_g2_inbox.py` 参数覆盖）。

**禁止**把未测的猜测 Hz 填进 JSON 冒充实测。

流程总览：`06_docs/G2_资源门禁_用户动作.md`。
