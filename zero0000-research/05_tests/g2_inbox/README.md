# G2 inbox（投放实测数据）

把 Day-1 之后的 **时钟 JSON** 与 **SPI CSV** 放进本目录，然后：

```bash
cd zero0000-research
python3 scripts/ingest_g2_inbox.py
python3 scripts/apply_g0_backfill.py          # dry-run
python3 scripts/apply_g0_backfill.py --apply  # 写 G0 + 结论卡；SPI 仅上电加 --power-on-only
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

### 快速写钟（有示波器读数时）

```bash
# 计划 B 例：ADC 与 DACCLK 均为 245.76 MHz（须是你测到的数）
python3 scripts/mk_g2_clocks.py --c2 245.76e6 --c3 245.76e6 --confirm-measured
# 或 CSV：两列 id,hz
python3 scripts/mk_g2_clocks.py --from-csv readings.csv --confirm-measured
```

无 `--confirm-measured` **不会**写入 inbox 根（防把先验当实测）。格式样例见 `examples/g2_clocks.planA.example.json` / `planB`（ingest **忽略** examples/）。

### 示波器截图 OCR（可选）

```bash
# 把屏幕照片放入本目录后列出候选 Hz，人眼核对再写入
python3 scripts/ocr_scope_hz.py 05_tests/g2_inbox/scope_c2.jpg
python3 scripts/ocr_scope_hz.py 05_tests/g2_inbox/scope_c2.jpg --as-c2 0 --as-c3-same \
  --write-clocks --confirm-measured
```

SPI CSV 列名：默认 `SCLK,MOSI,SEN,SDENB,SPI_LE`；也可用 Saleae 风格（`SPI_CLK`/`SDATA`/`ADC_CS`/…）。ingest 默认 `--auto-map`，也可用参数覆盖。

**禁止**把未测的猜测 Hz 填进 JSON，或把 `examples/*.csv` 冒充实测。

合成列名演练见 `examples/README.md`。流程总览：`05_tests/G2_投放三步.md`。
