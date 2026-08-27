# 无实机时的流水线测试

本目录包含**合成参考数据**，用于验证分析脚本能否正常运行。

**警告**：`eeprom_synthetic_reference.bin` **不是**从目标设备读取的数据，不得用于协议逆向或身份识别。

## 生成

```bash
python3 scripts/build_eeprom_synthetic.py
python3 scripts/analyze_eeprom.py   # 无 captures/eeprom.bin 时自动使用本夹具
```

## 真实数据

将真实转储放到 `../captures/eeprom.bin`，分析脚本会优先使用真实文件。
