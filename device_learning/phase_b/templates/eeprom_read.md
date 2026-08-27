# EEPROM 读取步骤

1. 断电，定位 USB 控制器附近 8 脚 SOIC 器件
2. 用 CH341A 或 I2C 工具读取
3. 保存到 `phase_b/captures/eeprom.bin`
4. 记录 SHA256 到 `manifests/eeprom_meta.json`

详见公开 24LC64 / CY7C68013A 引导设计文档。
