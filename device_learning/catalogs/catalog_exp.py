"""Experiment protocol catalog (phase C — requires hardware)."""
from catalogs import make_entry

LAYER = "exp"


def _e(i, m, d, s, b, ev):
    return make_entry(i, LAYER, m, d, s, b, ev)


ENTRIES = [
    _e("EXP-001-EEPROM-DUMP", "capture", "Read serial EEPROM to binary file", "not_started", "Need programmer", "phase_b/templates/eeprom_read.md"),
    _e("EXP-002-USB-ENUM", "capture", "Capture USB enumeration traffic", "candidate", "pcap present; deeper vendor-req table open", "phase_b/captures/usb_enum.pcapng"),
    _e("EXP-003-USB-SESSION", "capture", "Capture config+acquire session", "candidate", "pcap present; command semantics open", "phase_b/captures/usb_session.pcapng"),
    _e("EXP-004-PIN-FIFO", "verify", "Probe Slave FIFO signals vs REF catalog", "not_started", "Need scope", "pin_hypothesis.json BRG-001..009"),
    _e("EXP-005-PIN-ADC", "verify", "Probe ADC serial interface timing", "not_started", "Need scope", "REF-ADC-SPI-*"),
    _e("EXP-006-RELAY-TOGGLE", "verify", "Toggle relay and measure coax path", "not_started", "Need signal source", "SIG-002-RELAY-MATRIX"),
    _e("EXP-007-COUPLING", "verify", "AC/DC coupling switch behavior", "not_started", "Need relay command or manual", "SIG-006-COUPLING"),
    _e("EXP-008-SINE-IN", "verify", "Apply known sine, check digitized output", "not_started", "Need AWG+driver", "SIG-007-SAMPLE-WIDTH"),
    _e("EXP-009-CLOCK-IFCLK", "verify", "Measure IFCLK frequency at FPGA", "not_started", "Need freq counter", "REF-USB-SLAVE-FIFO-IFCLK"),
    _e("EXP-010-8051-DISASM", "analysis", "Disassemble firmware from EEPROM slice", "not_started", "Depends EXP-001", "scan_firmware_stub.py"),
    _e("EXP-011-PROTO-TABLE", "analysis", "Build command byte table from pcap", "not_started", "Depends EXP-003", "protocol_log_template.json"),
    _e("EXP-012-VIDPID", "analysis", "Record VID/PID from descriptor or EEPROM", "not_started", "Depends EXP-001/002", "eeprom_layout_ref.json"),
    _e("EXP-013-ENDPOINT-MAP", "analysis", "Map bulk IN/OUT endpoint numbers", "confirmed", None, "usb_protocol_decode.json"),
    _e("EXP-014-DATA-FRAME", "analysis", "Determine sample packing in USB stream", "not_started", "Depends EXP-008", "SIG-018-DATA-PACK"),
    _e("EXP-015-BRG-UPGRADE", "meta", "Upgrade hypothesis bridges to confirmed", "not_started", "Needs EXP-004..008", "bridge_matrix.json"),
]
