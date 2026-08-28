# scripts 使用说明

在仓库任意目录均可；推荐：

```bash
cd zero0000-research
python3 scripts/analyze_mcs.py          # MCS→结构/IDCODE（默认读 assets/firmware/*.mcs）
python3 scripts/parse_mcs.py assets/firmware/20230825_s2056.mcs --extract-bin /tmp/s2056.bin
python3 scripts/analyze_bitstream.py /tmp/s2056.bin   # 无参时若缺 .bin 会从 mcs 重建
python3 scripts/search_net_constants.py
python3 scripts/ft600_scaffold.py --help
python3 scripts/udp_probe.py --help
python3 scripts/l5_fft_check.py --help
```

正确 IDCODE：`XC7K160T = 0x0364C093`（勿用旧误记 `0x03631093`）。
