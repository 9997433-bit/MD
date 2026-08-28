# scripts 使用说明

在仓库任意目录均可；推荐：

```bash
cd zero0000-research
python3 scripts/analyze_mcs.py          # MCS→结构/IDCODE（默认读 assets/firmware/*.mcs）
python3 scripts/parse_mcs.py assets/firmware/20230825_s2056.mcs --extract-bin /tmp/s2056.bin
python3 scripts/analyze_bitstream.py /tmp/s2056.bin   # 无参时若缺 .bin 会从 mcs 重建
python3 scripts/search_net_constants.py
python3 scripts/analyze_bram_frames.py [/tmp/s2056.bin]  # BRAM 候选区密度（P2.5）
python3 scripts/search_spi_constants.py [/tmp/s2056.bin]   # FMC150 SPI 常量阴性/阳性扫描
python3 scripts/search_fmc150_mif_rom.py assets/firmware/20230825_s2056.bin  # KC705_DDS 整表 MIF
python3 scripts/decode_spi_capture.py --self-test            # G2 SPI CSV 译码自检
python3 scripts/decode_spi_capture.py capture.csv --json out.json
python3 scripts/g2_mode_infer.py --self-test                 # 钟+SPI → P1 等级建议
python3 scripts/g3_tone_analyze.py --self-test               # G3 单音落盘分析
python3 scripts/l5_fft_check.py --help
python3 scripts/ft600_scaffold.py --help
python3 scripts/udp_probe.py --help
```

正确 IDCODE：`XC7K160T = 0x0364C093`（勿用旧误记 `0x03631093`）。

- SPI 常量：`02_firmware/位流SPI常量搜索.md`
- KC705_DDS MIF：`02_firmware/KC705_DDS_SPI_MIF对照.md`
- BRAM 帧：`02_firmware/位流BRAM帧分析.md`
- G2/G3 模板：`05_tests/G2_时钟与SPI记录.md`、`G3_ADDA闭环记录.md`
- 通路图：`03_architecture/FPGA数据通路假说框图.md`
