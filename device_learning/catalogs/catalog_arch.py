"""System architecture layer catalog."""
from catalogs import make_entry

LAYER = "arch"


def _e(i, m, d, s, b, ev):
    return make_entry(i, LAYER, m, d, s, b, ev)


ENTRIES = [
    _e("ARCH-001-LAYERS", "topology", "Five-layer stack: HW → BIT → SIG → USB → HOST", "confirmed", None, "system_map.json"),
    _e("ARCH-002-DATA-PATH", "topology", "Coax → relay → ADC → FPGA FIFO → USB → host", "candidate", "中间节点未实测", "system_map.json"),
    _e("ARCH-003-CONFIG-CHAIN", "config", "FPGA configured from bitstream at power-on", "confirmed", None, "device.bit present"),
    _e("ARCH-004-USB-BOOT", "config", "USB MCU boots firmware from EEPROM over I2C", "candidate", "EEPROM未转储", "eeprom_layout_ref.json"),
    _e("ARCH-005-CLOCK-USB", "clock", "24 MHz oscillator feeds USB controller", "confirmed", None, "hardware_bom XT600"),
    _e("ARCH-006-CLOCK-IF", "clock", "48 MHz IFCLK to FPGA from USB controller", "candidate", "未实测", "REF-USB-SLAVE-FIFO-IFCLK"),
    _e("ARCH-007-CLOCK-FPGA", "clock", "FPGA fabric clock domain(s)", "unknown", None, None),
    _e("ARCH-008-RESET-USB", "reset", "USB controller reset domain", "unknown", None, None),
    _e("ARCH-009-RESET-FPGA", "reset", "FPGA GRESTORE in config sequence", "confirmed", None, "frame_summary cmd_sequence"),
    _e("ARCH-010-MEM-SRAM", "memory", "External SRAM buffer between USB and FPGA", "candidate", "容量未读", "hardware_bom U-SRAM"),
    _e("ARCH-011-MEM-FIFO", "memory", "FPGA internal FIFO for sample buffering", "hypothesis", "需BRAM解码", "SIG-004-PATH-FIFO"),
    _e("ARCH-012-CHANNELS", "topology", "Four parallel input channels", "candidate", None, "four coax + four ADC"),
    _e("ARCH-013-RELAY-CTRL", "control", "FPGA GPIO drives relay coils", "hypothesis", "需实验", "BRG-013"),
    _e("ARCH-014-DSUB-AUX", "interface", "D-sub auxiliary port via KS245 transceiver", "candidate", "功能未知", "hardware_bom U513"),
    _e("ARCH-015-BIT-LOAD", "config", "WCFG→FDRI→START configuration pipeline", "confirmed", None, "frame_summary packets"),
]
