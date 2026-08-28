# scripts 使用说明

在仓库任意目录均可；推荐：

```bash
cd zero0000-research
python3 scripts/analyze_mcs.py          # MCS→结构/IDCODE（默认读 assets/firmware/*.mcs）
python3 scripts/parse_mcs.py assets/firmware/20230825_s2056.mcs --extract-bin /tmp/s2056.bin
python3 scripts/analyze_bitstream.py /tmp/s2056.bin   # 无参时若缺 .bin 会从 mcs 重建
python3 scripts/search_net_constants.py
python3 scripts/search_spi_constants.py [/tmp/s2056.bin]   # FMC150 SPI 常量阴性/阳性扫描
python3 scripts/decode_spi_capture.py --self-test            # G2 SPI CSV 译码自检
python3 scripts/decode_spi_capture.py capture.csv --json out.json
python3 scripts/ft600_scaffold.py --help
python3 scripts/udp_probe.py --help
python3 scripts/l5_fft_check.py --help
```

正确 IDCODE：`XC7K160T = 0x0364C093`（勿用旧误记 `0x03631093`）。

SPI 常量搜索结论写入 `02_firmware/位流SPI常量搜索.md`；G2 记录模板见 `05_tests/G2_时钟与SPI记录.md`。
