# 无实机时的流水线测试

本目录包含**合成参考数据**，用于验证分析脚本能否正常运行。

**警告**：夹具 **不是**从目标设备读取的数据，不得用于协议逆向或身份识别。

| 文件 | 用途 |
|------|------|
| `eeprom_synthetic_reference.bin` | FX2LP C2 布局合成 EEPROM（8192 B） |
| `usb_enum_synthetic_reference.pcapng` | 最小合法 pcapng 壳（非真实 USB 流量） |

## 生成

```bash
python3 scripts/build_eeprom_synthetic.py
python3 scripts/build_pcap_synthetic.py
```

## 流水线演练

```bash
make dryrun       # EEPROM 合成路径
make dryrun-usb   # USB 抓包合成路径
```

合成文件放入 `captures/` 时会被识别为夹具，**不会**升级为 `observed` 或触发阶段 B 进展。

## 真实数据

将真实转储放到 `../captures/`，分析脚本会优先使用真实文件。
