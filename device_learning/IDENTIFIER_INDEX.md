# Identifier 索引（自动生成）

**生成时间**：2026-08-28 08:51 UTC

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## HW (32)

| ID | Status | Description |
|----|--------|-------------|
| `HW-001-FPGA-DEVICE` | confirmed | Xilinx Spartan XC3S200 FPGA |
| `HW-002-FPGA-PACKAGE` | confirmed | FT256 fine-pitch BGA package |
| `HW-003-USB-CONTROLLER` | confirmed | Cypress CY7C68013A USB 2.0 controller |
| `HW-004-USB-PACKAGE` | confirmed | 128-pin TQFP package |
| `HW-005-ADC-PRIMARY` | candidate | ADS1271 family 24-bit delta-sigma ADC |
| `HW-006-ADC-COUNT` | candidate | Four ADC channels |
| `HW-007-ADC-RESOLUTION` | candidate | 24-bit sampling resolution |
| `HW-008-RELAY-ARRAY` | confirmed | Omron G6JU-2FS-Y signal relay array |
| `HW-009-RELAY-COUNT` | confirmed | Twelve relay units |
| `HW-010-RELAY-VOLTAGE` | confirmed | 3V DC coil drive |
| `HW-011-BUS-TRANSCEIVER` | confirmed | KS245 octal bus transceiver |
| `HW-012-EEPROM` | candidate | Serial EEPROM for USB firmware boot |
| `HW-013-EEPROM-CAPACITY` | unknown | Likely 24LC64 (8KB) |
| `HW-014-CRYSTAL-USB` | candidate | 24MHz USB controller crystal |
| `HW-015-CRYSTAL-FPGA` | unknown | FPGA clock source |
| `HW-016-INTERFACE-COAX` | confirmed | Four coaxial analog inputs |
| `HW-017-INTERFACE-USB` | confirmed | USB Type-B device port |
| `HW-018-INTERFACE-DSUB` | confirmed | D-sub multi-pin connector |
| `HW-019-BOARD-REVISION` | confirmed | PCB revision silkscreen |
| `HW-020-BOARD-SERIAL` | confirmed | Barcode serial label |
| `HW-021-POWER-REGULATOR` | candidate | Voltage regulators |
| `HW-022-POWER-TANTALUM` | confirmed | 470uF tantalum bulk capacitors |
| `HW-023-MEMORY-SRAM` | confirmed | ISSI SRAM near FPGA |
| `HW-024-MANUFACTURER-SILK` | confirmed | OEM silkscreen logo |
| `HW-025-COPYRIGHT-YEAR` | confirmed | Copyright 2011 |
| `HW-026-MOUNTING-HOLES` | confirmed | Four corner mounting holes |
| `HW-027-GROUND-PLANE` | confirmed | Gold-plated ground frame |
| `HW-028-SIGNAL-ROUTING` | candidate | Relay matrix analog routing |
| `HW-029-ANALOG-FRONTEND` | candidate | Passive RC/L before ADC |
| `HW-030-COMPLIANCE` | confirmed | CE / UL recognition marks |
| `HW-031-CONNECTOR-J600` | confirmed | J600 SMT pad array |
| `HW-032-CONNECTOR-J603` | confirmed | J603 SMT pad array |

## BIT (78)

| ID | Status | Description |
|----|--------|-------------|
| `BIT-001-FORMAT` | confirmed | Xilinx BIT bitstream format |
| `BIT-002-FILE-SIZE` | confirmed | 131046 bytes total |
| `BIT-003-SHA256` | confirmed | 63cd3874297407bceedb524909d919dd35ba8a16639573a1af81721aed4fc3f5 |
| `BIT-004-SOURCE-DESIGN` | confirmed | Source NCD design name (redacted in manifests) |
| `BIT-005-TARGET-DEVICE` | confirmed | Spartan-3 XC3S200 |
| `BIT-006-PACKAGE` | confirmed | FT256 package |
| `BIT-007-BUILD-DATE` | confirmed | 2011/06/10 |
| `BIT-008-BUILD-TIME` | confirmed | 12:44:47 |
| `BIT-009-USER-ID` | confirmed | 0xFFFFFFFF |
| `BIT-010-DATA-LENGTH` | confirmed | Config data 0x1FF88 bytes |
| `BIT-011-SECTION-A` | confirmed | Section a device identifier |
| `BIT-012-SECTION-B` | confirmed | Section b design metadata |
| `BIT-013-SECTION-C` | confirmed | Section c part name |
| `BIT-014-SECTION-D` | confirmed | Section d configuration data |
| `BIT-015-CONFIG-OFFSET` | confirmed | Configuration data byte offset 94 |
| `BIT-SYNC-WORD` | confirmed | Sync word 0xAA995566 |
| `BIT-IDCODE` | confirmed | IDCODE 0x01414093 (Spartan-3 XC3S200) |
| `BIT-FLR` | confirmed | Frame Length Register = 52 words |
| `BIT-COR` | confirmed | COR register 0x40003FE5 |
| `BIT-CRC` | confirmed | CRC value 0x00005F57 |
| `BIT-CMD-SEQUENCE` | confirmed | RCRC→SWITCH→WCFG→GRESTORE→DGHIGH→START→DESYNCH |
| `BIT-FDRI-WORD-COUNT` | confirmed | FDRI payload 32648 words |
| `BIT-FRAME-COUNT-EST` | confirmed | Estimated 627 configuration frames (FDRI/FLR split) |
| `FRM-001-FORMAT` | candidate | Spartan-3 Type-1/Type-2 frame format |
| `FRM-002-COUNT` | candidate | Estimated 627 configuration frames |
| `FRM-003-WORD-WIDTH` | confirmed | 16-bit frame words |
| `FRM-004-TYPE1` | candidate | Type-1 write frames |
| `FRM-005-TYPE2` | candidate | Type-2 noop/pad frames |
| `FRM-006-STARTUP` | unknown | Startup clock cycles |
| `FRM-007-CRC` | confirmed | CRC register 0x00005F57 |
| `FRM-008-FAR` | unknown | Frame Address Register targets |
| `FRM-009-PIPELINE` | unknown | Pipeline register settings |
| `FRM-010-PADDING` | candidate | Padding/unused config bits |
| `FRM-011-FAR-WRITE-COUNT` | confirmed | Single explicit FAR write (0x00000000) |
| `FRM-012-FAR-COLUMN-ADDR` | confirmed | FAR Column Address field = 0 (logic & I/O block) |
| `FRM-013-FAR-MAJOR-MINOR` | confirmed | FAR start Major=0 / Minor=0 |
| `FRM-014-FAR-AUTOINC` | candidate | Per-frame FAR via internal auto-increment |
| `FRM-015-FRAME-LENGTH` | confirmed | Frame length 52 words (FLR register) |
| `FRM-016-FRAME-COUNT-EST` | candidate | Estimated 627 configuration frames |
| `FRM-017-PAD-FRAME` | candidate | Trailing pad frame per spec |
| `FRM-018-COLUMN-ADDR-DIST` | candidate | Explicit frame writes confined to Column Address 0 |
| `FRM-019-LOGIC-COLUMN-EST` | candidate | ~33 logic columns (candidate estimate) |
| `FRM-020-REG-WRITE-SET` | confirmed | Config register write set CMD/FLR/COR/IDCODE/MASK/FAR/CTL/CRC |
| `FRM-021-FAR-DIST` | candidate | FAR address value distribution |
| `FRM-022-TYPE1-REG-TOP` | candidate | Top Type-1 register write targets |
| `FRM-023-ZERO-RATIO` | confirmed | Zero-word padding ratio in config |
| `FRM-024-CLASS-COUNTS` | candidate | Frame word class histogram |
| `FRM-025-IO-BLOCK-WRITES` | unknown | IO block FAR writes |
| `FRM-026-CLB-BLOCK-WRITES` | unknown | CLB block FAR writes |
| `FRM-027-BRAM-BLOCK-WRITES` | unknown | BRAM block FAR writes |
| `FRM-028-CONFIG-ORDER` | unknown | Configuration write ordering |
| `FRM-029-DONE-PIPE` | unknown | DONE pipeline settings |
| `FRM-030-WAKEUP` | unknown | Startup wakeup sequence |
| `IOB-001-ACTIVE-COUNT` | candidate | Candidate IOB config words: 223 |
| `IOB-002-INPUTS` | unknown | Input-configured IOB pins |
| `IOB-003-OUTPUTS` | unknown | Output-configured IOB pins |
| `IOB-004-BIDIR` | unknown | Bidirectional IOB pins |
| `IOB-005-USB-FIFO` | hypothesis | USB Slave FIFO bus pins |
| `IOB-006-ADC-IF` | hypothesis | ADC interface pins |
| `IOB-007-RELAY-GPIO` | hypothesis | Relay control GPIO |
| `IOB-008-CLOCK` | unknown | Global clock input pins |
| `IOB-009-RESET` | unknown | Reset input pins |
| `IOB-010-UNUSED` | unknown | Unconfigured pins |
| `IOB-011-BANK-0` | unknown | IO Bank 0 config |
| `IOB-012-BANK-1` | unknown | IO Bank 1 config |
| `IOB-013-BANK-2` | unknown | IO Bank 2 config |
| `IOB-014-BANK-3` | unknown | IO Bank 3 config |
| `IOB-015-PULL` | unknown | Pull-up/down settings |
| `CLK-001-GCLK` | unknown | Global clock buffer usage |
| `CLK-002-DIST` | unknown | Clock tree distribution |
| `CLK-003-DLL` | unknown | DLL configuration |
| `CLK-004-RESET` | unknown | Global reset network |
| `CLK-005-DOMAINS` | unknown | Clock domain count |
| `MEM-001-BRAM` | unknown | Block RAM instances |
| `MEM-002-BRAM-INIT` | unknown | BRAM init content |
| `MEM-003-DIST-RAM` | unknown | Distributed RAM |
| `MEM-004-FIFO` | hypothesis | FIFO blocks |
| `MEM-005-ROM` | unknown | ROM init tables |

## SIGNAL (19)

| ID | Status | Description |
|----|--------|-------------|
| `SIG-USB-DIFF-PAIR` | candidate | USB differential data pair between the connector and the FPGA |
| `SIG-REF-CLOCK` | candidate | Reference clock distributed from the on-board oscillator to the FPGA |
| `SIG-CONFIG-BOOT` | candidate | FPGA configuration/boot lines from the config memory |
| `SIG-ACQ-CHANNEL` | unknown | Acquisition channel from the analog front-end into the fabric |
| `SIG-POWER-RAILS` | unknown | Core / I/O rail voltages presented to the FPGA |
| `SIG-PROTOCOL-FRAMING` | candidate | Application-level framing carried over the USB link |
| `SIG-INPUT-CONNECTOR` | candidate | Analog input interface / connector at the board edge |
| `SIG-INPUT-PROTECTION` | unknown | Input over-voltage protection / clamp on the front-end |
| `SIG-COUPLING-MODE` | unknown | Input coupling selection (AC / DC) ahead of the gain stage |
| `SIG-COUPLING-RELAY` | unknown | Relay switching input coupling / range in the signal path |
| `SIG-RELAY-DRIVE` | unknown | Control/drive line that actuates the signal-path relay |
| `SIG-ATTENUATOR` | unknown | Input attenuator / divider setting the measurement range |
| `SIG-PREAMP-GAIN` | unknown | Front-end amplifier / buffer (possibly programmable-gain) stage |
| `SIG-ANTIALIAS-FILTER` | unknown | Anti-alias low-pass filter ahead of the ADC |
| `SIG-ADC-INTERFACE` | unknown | ADC device and its digital data interface into the fabric |
| `SIG-ADC-RESOLUTION` | unknown | Sampling bit width / resolution of the ADC |
| `SIG-ADC-SAMPLE-RATE` | unknown | ADC sampling rate as configured on the board |
| `SIG-ADC-REFERENCE` | unknown | ADC voltage reference source |
| `SIG-ADC-TO-INTERFACE` | not_started | Data path from ADC through the fabric out to the host interface |

## USB (34)

| ID | Status | Description |
|----|--------|-------------|
| `FW-EEPROM-SYNTHETIC-FIXTURE` | candidate | Synthetic EEPROM for pipeline test only |
| `FW-EEPROM-LAYOUT-REF` | candidate | Public FX2LP EEPROM field layout reference |
| `FW-EEPROM-BOOT-BYTE-RULE` | candidate | Boot config byte semantics (0xC0/0xC2) |
| `FW-EEPROM-FW-OFFSET` | candidate | Typical 8051 firmware start offset 0x10 in EEPROM |
| `FW-MCU-CORE-IMAGE` | missing | 8051-compatible microcontroller firmware image |
| `FW-MCU-RESET-VECTOR` | missing | Reset vector / boot entry of the MCU firmware |
| `FW-MCU-CODE-XRAM-MAP` | missing | Code / external-RAM address map of the MCU |
| `FW-MCU-I2C-BOOT-PATH` | missing | MCU boot path loading from the serial EEPROM over I2C |
| `FW-MCU-RENUMERATION` | candidate | USB re-numeration after FX2 RAM load: 0x7317 → 0x744f |
| `FW-EEPROM-IMAGE` | missing | Serial EEPROM contents image |
| `FW-EEPROM-CONFIG-BYTE` | missing | EEPROM leading boot-configuration byte |
| `FW-EEPROM-VIDPID` | missing | VID/PID fields possibly stored in the EEPROM |
| `FW-EEPROM-DESC-OVERRIDE` | missing | Descriptor-override data possibly held in the EEPROM |
| `FW-EEPROM-BOOT-FORMAT` | missing | EEPROM boot-format selector (boot_config_byte at offset 0x00) |
| `FW-EEPROM-DID-FIELD` | missing | Device release / Device ID override word (did field at offset 0x05) |
| `FW-EEPROM-FW-RECORDS` | missing | Firmware image data records / firmware size (C2 data-record region) |
| `FW-FPGA-BITSTREAM` | candidate | FPGA bitstream file (firmware/device.bit) |
| `FW-FPGA-CONFIG-IFACE` | unknown | FPGA configuration interface / load source |
| `PROTO-DESC-DEVICE` | confirmed | USB device descriptor VID=0x3923 PID=0x744f bcdDevice=0x0001 |
| `PROTO-DESC-CONFIG` | confirmed | USB configuration descriptor: 1 interface, bmAttributes=0x80 |
| `PROTO-DESC-INTERFACE` | confirmed | Interface 0 vendor-specific (0xff), 4 endpoints, alt=0 |
| `PROTO-DESC-STRING` | candidate | USB string descriptors (partial; serial candidate present) |
| `PROTO-EP-MAP` | confirmed | Endpoints: bulk 0x01 OUT, 0x81 IN, 0x06 OUT, 0x84 IN (512 B) |
| `PROTO-EP-BULK-IN` | confirmed | Bulk IN endpoints 0x81 and 0x84, wMaxPacketSize=512 |
| `PROTO-EP-BULK-OUT` | confirmed | Bulk OUT endpoints 0x01 and 0x06, wMaxPacketSize=512 |
| `PROTO-EP-INTERRUPT` | candidate | No interrupt endpoint in observed interface descriptor |
| `PROTO-EP-ALT-SETTINGS` | candidate | Only bAlternateSetting=0 observed |
| `PROTO-XFER-MODE` | confirmed | Acquisition stream uses bulk transfers (not isochronous) |
| `PROTO-CTRL-VENDOR-REQ` | candidate | Vendor-specific control-request surface |
| `DRV-HOST-MODULE` | not_started | Host-side USB driver module |
| `DRV-INF-BINDING` | not_started | Driver INF binding (VID/PID match) |
| `DRV-IOCTL-SURFACE` | not_started | Driver IOCTL interface surface |
| `DRV-FIRMWARE-LOADER` | candidate | Host-side firmware downloader |
| `DRV-PIPE-EP-BIND` | candidate | Driver pipe-to-endpoint binding |

## REF (24)

| ID | Status | Description |
|----|--------|-------------|
| `REF-USB-SLAVE-FIFO-SLRD` | candidate | SLRD: slave FIFO read strobe driven by the external master (FPGA) |
| `REF-USB-SLAVE-FIFO-SLWR` | candidate | SLWR: slave FIFO write strobe driven by the external master (FPGA) |
| `REF-USB-SLAVE-FIFO-SLOE` | candidate | SLOE: slave FIFO output enable gating the FD data bus drivers |
| `REF-USB-SLAVE-FIFO-SLCS` | candidate | SLCS#: slave FIFO chip select qualifying SLRD/SLWR/PKTEND |
| `REF-USB-SLAVE-FIFO-FLAGA` | candidate | FLAGA: FIFO status flag (indexed/programmable, e.g. programmable-level) |
| `REF-USB-SLAVE-FIFO-FLAGB` | candidate | FLAGB: FIFO status flag (typically full flag in default config) |
| `REF-USB-SLAVE-FIFO-FLAGC` | candidate | FLAGC: FIFO status flag (typically empty flag in default config) |
| `REF-USB-SLAVE-FIFO-FIFOADR` | candidate | FIFOADR[1:0]: 2-bit address selecting the active endpoint FIFO (EP2/4/6/8) |
| `REF-USB-SLAVE-FIFO-FD-BUS` | candidate | FD[15:0]: bidirectional slave FIFO data bus (8-bit or 16-bit word mode) |
| `REF-USB-SLAVE-FIFO-PKTEND` | candidate | PKTEND: strobe committing a short (non-full) IN packet to USB |
| `REF-USB-SLAVE-FIFO-IFCLK` | candidate | IFCLK: interface clock, internal 30/48 MHz output or 5-48 MHz external input |
| `REF-ADC-SPI-DOUT` | candidate | DOUT: serial conversion data output from the ADC toward the fabric |
| `REF-ADC-SPI-DRDY` | candidate | DRDY: data-ready indication (shared DOUT/DRDY pin in SPI format) |
| `REF-ADC-SPI-SCLK` | candidate | SCLK: serial shift clock for the ADC data interface |
| `REF-ADC-SPI-FSYNC` | candidate | FSYNC: frame-sync signal framing each conversion word (frame-sync format) |
| `REF-ADC-SPI-DIN` | candidate | DIN: serial data input used for daisy-chaining multiple ADCs |
| `REF-ADC-MASTER-CLK` | candidate | CLK: ADC master/modulator clock input setting the data rate |
| `REF-ADC-MODE-PINS` | candidate | MODE pin(s): operating-mode strap (high-speed / high-resolution / low-power) |
| `REF-ADC-FORMAT-PINS` | candidate | FORMAT[2:0]: interface-format straps selecting SPI vs frame-sync and chaining |
| `REF-ADC-SYNC-PIN` | candidate | SYNC/PDWN: conversion synchronisation / power-down control input |
| `REF-EEPROM-I2C-SCL` | candidate | SCL: I2C clock line between the USB controller and the boot EEPROM |
| `REF-EEPROM-I2C-SDA` | candidate | SDA: I2C data line between the USB controller and the boot EEPROM |
| `REF-EEPROM-I2C-BOOT-ADDR` | candidate | EEPROM I2C device address convention distinguishing small/large boot EEPROMs |
| `REF-EEPROM-I2C-BOOT-BYTE` | candidate | Leading boot-configuration byte (0xC0/0xC2 convention) selecting the boot mode |

## ARCH (15)

| ID | Status | Description |
|----|--------|-------------|
| `ARCH-001-LAYERS` | confirmed | Five-layer stack: HW → BIT → SIG → USB → HOST |
| `ARCH-002-DATA-PATH` | candidate | Coax → relay → ADC → FPGA FIFO → USB → host |
| `ARCH-003-CONFIG-CHAIN` | confirmed | FPGA configured from bitstream at power-on |
| `ARCH-004-USB-BOOT` | candidate | USB MCU boots firmware from EEPROM over I2C |
| `ARCH-005-CLOCK-USB` | confirmed | 24 MHz oscillator feeds USB controller |
| `ARCH-006-CLOCK-IF` | candidate | 48 MHz IFCLK to FPGA from USB controller |
| `ARCH-007-CLOCK-FPGA` | unknown | FPGA fabric clock domain(s) |
| `ARCH-008-RESET-USB` | unknown | USB controller reset domain |
| `ARCH-009-RESET-FPGA` | confirmed | FPGA GRESTORE in config sequence |
| `ARCH-010-MEM-SRAM` | candidate | External SRAM buffer between USB and FPGA |
| `ARCH-011-MEM-FIFO` | hypothesis | FPGA internal FIFO for sample buffering |
| `ARCH-012-CHANNELS` | candidate | Four parallel input channels |
| `ARCH-013-RELAY-CTRL` | hypothesis | FPGA GPIO drives relay coils |
| `ARCH-014-DSUB-AUX` | candidate | D-sub auxiliary port via KS245 transceiver |
| `ARCH-015-BIT-LOAD` | confirmed | WCFG→FDRI→START configuration pipeline |

## LEARN (20)

| ID | Status | Description |
|----|--------|-------------|
| `LEARN-001-GOAL` | confirmed | Build auditable static learning package |
| `LEARN-002-STOP` | confirmed | Directory complete != vendor equivalence |
| `LEARN-003-HW-BOM` | confirmed | Read hardware BOM and photo index |
| `LEARN-004-BIT-HEADER` | confirmed | Understand Xilinx BIT container sections a-e |
| `LEARN-005-BIT-PACKETS` | confirmed | Trace Spartan-3 config packet stream |
| `LEARN-006-FRAME-HEUR` | candidate | Interpret frame/IOB heuristic limits |
| `LEARN-007-REF-DESIGN` | candidate | Compare REF catalog to public TRMs |
| `LEARN-008-SYSTEM-MAP` | candidate | Follow data path in system_map.json |
| `LEARN-009-EEPROM-LAYOUT` | candidate | Study FX2LP EEPROM boot layout |
| `LEARN-010-USB-PROTO` | candidate | USB protocol from capture |
| `LEARN-011-8051-DISASM` | not_started | 8051 firmware reverse engineering |
| `LEARN-012-PIN-TEST` | not_started | Pin hypothesis verification experiments |
| `LEARN-013-RELAY-TEST` | not_started | Relay switching experiment design |
| `LEARN-014-BRAM-DECODE` | unknown | BRAM init extraction from bitstream |
| `LEARN-015-OPEN-REIMPL` | not_started | Open-source behavioral reimplementation |
| `LEARN-016-NULL-BRIDGE` | confirmed | Understand forced null bridges policy |
| `LEARN-017-CROSSREF` | confirmed | Navigate cross-layer themes |
| `LEARN-018-PHOTO-INDEX` | confirmed | Map photos to components |
| `LEARN-019-REGENERATE` | confirmed | Regenerate ledger and run pytest |
| `LEARN-020-BOUNDARY` | confirmed | Document unknowns honestly |

## EXP (15)

| ID | Status | Description |
|----|--------|-------------|
| `EXP-001-EEPROM-DUMP` | not_started | Read serial EEPROM to binary file |
| `EXP-002-USB-ENUM` | candidate | Capture USB enumeration traffic |
| `EXP-003-USB-SESSION` | candidate | Capture config+acquire session |
| `EXP-004-PIN-FIFO` | not_started | Probe Slave FIFO signals vs REF catalog |
| `EXP-005-PIN-ADC` | not_started | Probe ADC serial interface timing |
| `EXP-006-RELAY-TOGGLE` | not_started | Toggle relay and measure coax path |
| `EXP-007-COUPLING` | not_started | AC/DC coupling switch behavior |
| `EXP-008-SINE-IN` | not_started | Apply known sine, check digitized output |
| `EXP-009-CLOCK-IFCLK` | not_started | Measure IFCLK frequency at FPGA |
| `EXP-010-8051-DISASM` | not_started | Disassemble firmware from EEPROM slice |
| `EXP-011-PROTO-TABLE` | not_started | Build command byte table from pcap |
| `EXP-012-VIDPID` | not_started | Record VID/PID from descriptor or EEPROM |
| `EXP-013-ENDPOINT-MAP` | confirmed | Map bulk IN/OUT endpoint numbers |
| `EXP-014-DATA-FRAME` | not_started | Determine sample packing in USB stream |
| `EXP-015-BRG-UPGRADE` | not_started | Upgrade hypothesis bridges to confirmed |

**合计**：237 条

