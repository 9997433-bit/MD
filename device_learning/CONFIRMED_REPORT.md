# 已确认项报告（自动生成）

**生成时间**：2026-08-27 16:04 UTC

**confirmed 总数**：68 条

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为

以下项有静态证据支撑；不含运行行为等价声明。

## HW (22)

| Identifier | Evidence |
|------------|----------|
| `HW-001-FPGA-DEVICE` | bitstream header + photo |
| `HW-002-FPGA-PACKAGE` | device string 3s200ft256 |
| `HW-003-USB-CONTROLLER` | photo chip marking |
| `HW-004-USB-PACKAGE` | photo marking 128AXI |
| `HW-008-RELAY-ARRAY` | photo white relay packages |
| `HW-009-RELAY-COUNT` | photo count |
| `HW-010-RELAY-VOLTAGE` | relay marking 3V DC |
| `HW-011-BUS-TRANSCEIVER` | photo U613 marking |
| `HW-016-INTERFACE-COAX` | photo BNC jacks |
| `HW-017-INTERFACE-USB` | photo bottom edge |
| `HW-018-INTERFACE-DSUB` | photo AMP connector |
| `HW-019-BOARD-REVISION` | photo board labels |
| `HW-020-BOARD-SERIAL` | photo sticker |
| `HW-022-POWER-TANTALUM` | photo 477A marking |
| `HW-023-MEMORY-SRAM` | photo ISSI chip |
| `HW-024-MANUFACTURER-SILK` | photo logo text |
| `HW-025-COPYRIGHT-YEAR` | photo + bitstream date |
| `HW-026-MOUNTING-HOLES` | photo full board |
| `HW-027-GROUND-PLANE` | photo edge plating |
| `HW-030-COMPLIANCE` | photo compliance logos |
| `HW-031-CONNECTOR-J600` | photo pads |
| `HW-032-CONNECTOR-J603` | photo pads |

## BIT (31)

| Identifier | Evidence |
|------------|----------|
| `BIT-001-FORMAT` | file magic |
| `BIT-002-FILE-SIZE` | wc -c |
| `BIT-003-SHA256` | sha256sum |
| `BIT-004-SOURCE-DESIGN` | bitstream section a |
| `BIT-005-TARGET-DEVICE` | section a |
| `BIT-006-PACKAGE` | device string |
| `BIT-007-BUILD-DATE` | section b |
| `BIT-008-BUILD-TIME` | section b |
| `BIT-009-USER-ID` | section b |
| `BIT-010-DATA-LENGTH` | section d |
| `BIT-011-SECTION-A` | BIT parser |
| `BIT-012-SECTION-B` | BIT parser |
| `BIT-013-SECTION-C` | BIT parser |
| `BIT-014-SECTION-D` | BIT parser |
| `BIT-015-CONFIG-OFFSET` | frame_summary.json |
| `BIT-SYNC-WORD` | frame_summary.config_data.sync_word |
| `BIT-IDCODE` | frame_summary.packet_stream.registers.IDCODE |
| `BIT-FLR` | frame_summary.packet_stream.registers.FLR |
| `BIT-COR` | frame_summary.packet_stream.registers.COR |
| `BIT-CRC` | frame_summary.packet_stream.registers.CRC |
| `BIT-CMD-SEQUENCE` | frame_summary.packet_stream.cmd_sequence |
| `BIT-FDRI-WORD-COUNT` | frame_summary.packet_stream.fdri.word_count |
| `BIT-FRAME-COUNT-EST` | frame_summary.frame_analysis.estimated_frame_count |
| `FRM-003-WORD-WIDTH` | Spartan-3 spec |
| `FRM-007-CRC` | frame_summary |
| `FRM-011-FAR-WRITE-COUNT` | scan_spartan3_frames.py / frame_deep.json |
| `FRM-012-FAR-COLUMN-ADDR` | frame_deep.json (XAPP452 Fig.2 decode) |
| `FRM-013-FAR-MAJOR-MINOR` | frame_deep.json |
| `FRM-015-FRAME-LENGTH` | frame_deep.json register inventory |
| `FRM-020-REG-WRITE-SET` | frame_deep.json register inventory |
| `FRM-023-ZERO-RATIO` | frame_deep.json scan |

## ARCH (5)

| Identifier | Evidence |
|------------|----------|
| `ARCH-001-LAYERS` | system_map.json |
| `ARCH-003-CONFIG-CHAIN` | device.bit present |
| `ARCH-005-CLOCK-USB` | hardware_bom XT600 |
| `ARCH-009-RESET-FPGA` | frame_summary cmd_sequence |
| `ARCH-015-BIT-LOAD` | frame_summary packets |

## LEARN (10)

| Identifier | Evidence |
|------------|----------|
| `LEARN-001-GOAL` | README.md |
| `LEARN-002-STOP` | coverage.json |
| `LEARN-003-HW-BOM` | hardware_bom.json |
| `LEARN-004-BIT-HEADER` | bitstream_meta.json |
| `LEARN-005-BIT-PACKETS` | frame_summary.json |
| `LEARN-016-NULL-BRIDGE` | bridge_matrix.json |
| `LEARN-017-CROSSREF` | crossref_index.json |
| `LEARN-018-PHOTO-INDEX` | photo_index.json |
| `LEARN-019-REGENERATE` | generate_ledger.py |
| `LEARN-020-BOUNDARY` | OMISSIONS_AND_REMAINING.md |

