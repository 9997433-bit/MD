"""Hardware layer identifier catalog."""
from catalogs import make_entry

LAYER = "hw"


def _e(i, m, d, s, b, ev):
    return make_entry(i, LAYER, m, d, s, b, ev)


ENTRIES = [
    _e("HW-001-FPGA-DEVICE", "fpga", "Xilinx Spartan XC3S200 FPGA", "confirmed", None, "bitstream header + photo"),
    _e("HW-002-FPGA-PACKAGE", "fpga", "FT256 fine-pitch BGA package", "confirmed", None, "device string 3s200ft256"),
    _e("HW-003-USB-CONTROLLER", "usb", "Cypress CY7C68013A USB 2.0 controller", "confirmed", None, "photo chip marking"),
    _e("HW-004-USB-PACKAGE", "usb", "128-pin TQFP package", "confirmed", None, "photo marking 128AXI"),
    _e("HW-005-ADC-PRIMARY", "adc", "ADS1271 family 24-bit delta-sigma ADC", "candidate", "丝印需逐颗确认", "photo analog section"),
    _e("HW-006-ADC-COUNT", "adc", "Four ADC channels", "candidate", "需数芯片数量", "four coax inputs"),
    _e("HW-007-ADC-RESOLUTION", "adc", "24-bit sampling resolution", "candidate", "来自芯片系列规格", "ADS1271 datasheet family"),
    _e("HW-008-RELAY-ARRAY", "relay", "Omron G6JU-2FS-Y signal relay array", "confirmed", None, "photo white relay packages"),
    _e("HW-009-RELAY-COUNT", "relay", "Twelve relay units", "confirmed", None, "photo count"),
    _e("HW-010-RELAY-VOLTAGE", "relay", "3V DC coil drive", "confirmed", None, "relay marking 3V DC"),
    _e("HW-011-BUS-TRANSCEIVER", "bus", "KS245 octal bus transceiver", "confirmed", None, "photo U613 marking"),
    _e("HW-012-EEPROM", "storage", "Serial EEPROM for USB firmware boot", "candidate", "未直接拍到丝印", "standard design pattern"),
    _e("HW-013-EEPROM-CAPACITY", "storage", "Likely 24LC64 (8KB)", "unknown", "需读板", None),
    _e("HW-014-CRYSTAL-USB", "clock", "24MHz USB controller crystal", "candidate", "频率未实测", "reference design"),
    _e("HW-015-CRYSTAL-FPGA", "clock", "FPGA clock source", "unknown", "照片未清晰标注", None),
    _e("HW-016-INTERFACE-COAX", "interface", "Four coaxial analog inputs", "confirmed", None, "photo BNC jacks"),
    _e("HW-017-INTERFACE-USB", "interface", "USB Type-B device port", "confirmed", None, "photo bottom edge"),
    _e("HW-018-INTERFACE-DSUB", "interface", "D-sub multi-pin connector", "confirmed", "pin count TBD", "photo AMP connector"),
    _e("HW-019-BOARD-REVISION", "board", "PCB revision silkscreen", "confirmed", None, "photo board labels"),
    _e("HW-020-BOARD-SERIAL", "board", "Barcode serial label", "confirmed", None, "photo sticker"),
    _e("HW-021-POWER-REGULATOR", "power", "Voltage regulators", "candidate", "型号未全识别", "photo power section"),
    _e("HW-022-POWER-TANTALUM", "power", "470uF tantalum bulk capacitors", "confirmed", None, "photo 477A marking"),
    _e("HW-023-MEMORY-SRAM", "memory", "ISSI SRAM near FPGA", "confirmed", "容量未读", "photo ISSI chip"),
    _e("HW-024-MANUFACTURER-SILK", "board", "OEM silkscreen logo", "confirmed", None, "photo logo text"),
    _e("HW-025-COPYRIGHT-YEAR", "board", "Copyright 2011", "confirmed", None, "photo + bitstream date"),
    _e("HW-026-MOUNTING-HOLES", "mechanical", "Four corner mounting holes", "confirmed", None, "photo full board"),
    _e("HW-027-GROUND-PLANE", "mechanical", "Gold-plated ground frame", "confirmed", None, "photo edge plating"),
    _e("HW-028-SIGNAL-ROUTING", "signal", "Relay matrix analog routing", "candidate", "路由未验证", "photo layout"),
    _e("HW-029-ANALOG-FRONTEND", "signal", "Passive RC/L before ADC", "candidate", "元件值未读", "photo analog clusters"),
    _e("HW-030-COMPLIANCE", "board", "CE / UL recognition marks", "confirmed", None, "photo compliance logos"),
    _e("HW-031-CONNECTOR-J600", "connector", "J600 SMT pad array", "confirmed", "未焊接", "photo pads"),
    _e("HW-032-CONNECTOR-J603", "connector", "J603 SMT pad array", "confirmed", "未焊接", "photo pads"),
]
