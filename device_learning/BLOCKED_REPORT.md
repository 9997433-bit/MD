# 阻塞项报告（自动生成）

**生成时间**：2026-08-27 16:14 UTC

**阻塞总数**：98 条

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## missing (12)

| Identifier | Layer | Boundary |
|------------|-------|----------|
| `FW-MCU-CORE-IMAGE` | usb | no_dump |
| `FW-MCU-RESET-VECTOR` | usb | no_dump |
| `FW-MCU-CODE-XRAM-MAP` | usb | no_dump |
| `FW-MCU-I2C-BOOT-PATH` | usb | no_dump |
| `FW-MCU-RENUMERATION` | usb | no_dump |
| `FW-EEPROM-IMAGE` | usb | no_dump |
| `FW-EEPROM-CONFIG-BYTE` | usb | no_dump |
| `FW-EEPROM-VIDPID` | usb | no_dump |
| `FW-EEPROM-DESC-OVERRIDE` | usb | no_dump |
| `FW-EEPROM-BOOT-FORMAT` | usb | no_dump |
| `FW-EEPROM-DID-FIELD` | usb | no_dump |
| `FW-EEPROM-FW-RECORDS` | usb | no_dump |

## not_started (30)

| Identifier | Layer | Boundary |
|------------|-------|----------|
| `SIG-ADC-TO-INTERFACE` | signal | cross_layer |
| `PROTO-DESC-DEVICE` | usb | no_capture |
| `PROTO-DESC-CONFIG` | usb | no_capture |
| `PROTO-DESC-INTERFACE` | usb | no_capture |
| `PROTO-DESC-STRING` | usb | no_capture |
| `PROTO-CTRL-VENDOR-REQ` | usb | no_capture |
| `DRV-HOST-MODULE` | usb | no_binary |
| `DRV-INF-BINDING` | usb | no_binary |
| `DRV-IOCTL-SURFACE` | usb | no_binary |
| `DRV-FIRMWARE-LOADER` | usb | no_binary |
| `LEARN-010-USB-PROTO` | learn | Need pcap |
| `LEARN-011-8051-DISASM` | learn | Need eeprom.bin |
| `LEARN-012-PIN-TEST` | learn | Need hardware |
| `LEARN-013-RELAY-TEST` | learn | Need hardware |
| `LEARN-015-OPEN-REIMPL` | learn | Future phase D |
| `EXP-001-EEPROM-DUMP` | exp | Need programmer |
| `EXP-002-USB-ENUM` | exp | Need device+host |
| `EXP-003-USB-SESSION` | exp | Need official driver |
| `EXP-004-PIN-FIFO` | exp | Need scope |
| `EXP-005-PIN-ADC` | exp | Need scope |
| `EXP-006-RELAY-TOGGLE` | exp | Need signal source |
| `EXP-007-COUPLING` | exp | Need relay command or manual |
| `EXP-008-SINE-IN` | exp | Need AWG+driver |
| `EXP-009-CLOCK-IFCLK` | exp | Need freq counter |
| `EXP-010-8051-DISASM` | exp | Depends EXP-001 |
| `EXP-011-PROTO-TABLE` | exp | Depends EXP-003 |
| `EXP-012-VIDPID` | exp | Depends EXP-001/002 |
| `EXP-013-ENDPOINT-MAP` | exp | Depends EXP-002 |
| `EXP-014-DATA-FRAME` | exp | Depends EXP-008 |
| `EXP-015-BRG-UPGRADE` | exp | Needs EXP-004..008 |

## unknown (56)

| Identifier | Layer | Boundary |
|------------|-------|----------|
| `HW-013-EEPROM-CAPACITY` | hw | 需读板 |
| `HW-015-CRYSTAL-FPGA` | hw | 照片未清晰标注 |
| `FRM-006-STARTUP` | bit | 需帧级解码 |
| `FRM-008-FAR` | bit | 需完整解析 |
| `FRM-009-PIPELINE` | bit | — |
| `FRM-025-IO-BLOCK-WRITES` | bit | 需FAR解码 |
| `FRM-026-CLB-BLOCK-WRITES` | bit | 需FAR解码 |
| `FRM-027-BRAM-BLOCK-WRITES` | bit | 需FAR解码 |
| `FRM-028-CONFIG-ORDER` | bit | — |
| `FRM-029-DONE-PIPE` | bit | — |
| `FRM-030-WAKEUP` | bit | — |
| `IOB-002-INPUTS` | bit | — |
| `IOB-003-OUTPUTS` | bit | — |
| `IOB-004-BIDIR` | bit | — |
| `IOB-008-CLOCK` | bit | — |
| `IOB-009-RESET` | bit | — |
| `IOB-010-UNUSED` | bit | — |
| `IOB-011-BANK-0` | bit | — |
| `IOB-012-BANK-1` | bit | — |
| `IOB-013-BANK-2` | bit | — |
| `IOB-014-BANK-3` | bit | — |
| `IOB-015-PULL` | bit | — |
| `CLK-001-GCLK` | bit | — |
| `CLK-002-DIST` | bit | — |
| `CLK-003-DLL` | bit | — |
| `CLK-004-RESET` | bit | — |
| `CLK-005-DOMAINS` | bit | — |
| `MEM-001-BRAM` | bit | — |
| `MEM-002-BRAM-INIT` | bit | — |
| `MEM-003-DIST-RAM` | bit | — |
| `MEM-005-ROM` | bit | — |
| `SIG-ACQ-CHANNEL` | signal | no_capture |
| `SIG-POWER-RAILS` | signal | no_measurement |
| `SIG-PROTOCOL-FRAMING` | signal | no_capture |
| `SIG-INPUT-PROTECTION` | signal | no_measurement |
| `SIG-COUPLING-MODE` | signal | no_measurement |
| `SIG-COUPLING-RELAY` | signal | no_measurement |
| `SIG-RELAY-DRIVE` | signal | no_measurement |
| `SIG-ATTENUATOR` | signal | no_measurement |
| `SIG-PREAMP-GAIN` | signal | no_measurement |
| `SIG-ANTIALIAS-FILTER` | signal | no_measurement |
| `SIG-ADC-INTERFACE` | signal | no_measurement |
| `SIG-ADC-RESOLUTION` | signal | no_datasheet |
| `SIG-ADC-SAMPLE-RATE` | signal | no_datasheet |
| `SIG-ADC-REFERENCE` | signal | no_measurement |
| `FW-FPGA-CONFIG-IFACE` | usb | no_dump |
| `PROTO-EP-MAP` | usb | no_capture |
| `PROTO-EP-BULK-IN` | usb | no_capture |
| `PROTO-EP-BULK-OUT` | usb | no_capture |
| `PROTO-EP-INTERRUPT` | usb | no_capture |
| `PROTO-EP-ALT-SETTINGS` | usb | no_capture |
| `PROTO-XFER-MODE` | usb | no_capture |
| `DRV-PIPE-EP-BIND` | usb | cross_layer |
| `ARCH-007-CLOCK-FPGA` | arch | — |
| `ARCH-008-RESET-USB` | arch | — |
| `LEARN-014-BRAM-DECODE` | learn | No decoder |

## 解锁路线

见 `manifests/phase_roadmap.json` 与 `HARDWARE_HANDOFF.md`。

