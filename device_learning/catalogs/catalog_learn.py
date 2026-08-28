"""Learning objectives and study checklist catalog."""
from catalogs import make_entry

LAYER = "learn"


def _e(i, m, d, s, b, ev):
    return make_entry(i, LAYER, m, d, s, b, ev)


ENTRIES = [
    _e("LEARN-001-GOAL", "meta", "Build auditable static learning package", "confirmed", None, "README.md"),
    _e("LEARN-002-STOP", "meta", "Directory complete != vendor equivalence", "confirmed", None, "coverage.json"),
    _e("LEARN-003-HW-BOM", "topic", "Read hardware BOM and photo index", "confirmed", None, "hardware_bom.json"),
    _e("LEARN-004-BIT-HEADER", "topic", "Understand Xilinx BIT container sections a-e", "confirmed", None, "bitstream_meta.json"),
    _e("LEARN-005-BIT-PACKETS", "topic", "Trace Spartan-3 config packet stream", "confirmed", None, "frame_summary.json"),
    _e("LEARN-006-FRAME-HEUR", "topic", "Interpret frame/IOB heuristic limits", "candidate", "IOB mapping incomplete", "frame_analysis"),
    _e("LEARN-007-REF-DESIGN", "topic", "Compare REF catalog to public TRMs", "candidate", "Pins not verified", "catalog_ref.py"),
    _e("LEARN-008-SYSTEM-MAP", "topic", "Follow data path in system_map.json", "candidate", "Analog path unprobed", "system_map.json"),
    _e("LEARN-009-EEPROM-LAYOUT", "topic", "Study FX2LP EEPROM boot layout", "candidate", "No dump yet", "eeprom_layout_ref.json"),
    _e("LEARN-010-USB-PROTO", "topic", "USB protocol from capture", "candidate", "Framing 100% on EP01/81; 14 opcodes listed, meanings open", "usb_command_taxonomy.json"),
    _e("LEARN-011-8051-DISASM", "topic", "8051 firmware reverse engineering", "not_started", "Need eeprom.bin", "scan_firmware_stub.py"),
    _e("LEARN-012-PIN-TEST", "topic", "Pin hypothesis verification experiments", "not_started", "Need hardware", "pin_hypothesis.json"),
    _e("LEARN-013-RELAY-TEST", "topic", "Relay switching experiment design", "not_started", "Need hardware", "SIG-002-RELAY-MATRIX"),
    _e("LEARN-014-BRAM-DECODE", "topic", "BRAM init extraction from bitstream", "unknown", "No decoder", "MEM-001-BRAM"),
    _e("LEARN-015-OPEN-REIMPL", "topic", "Open-source behavioral reimplementation", "not_started", "Future phase D", "OMISSIONS"),
    _e("LEARN-016-NULL-BRIDGE", "topic", "Understand forced null bridges policy", "confirmed", None, "bridge_matrix.json"),
    _e("LEARN-017-CROSSREF", "topic", "Navigate cross-layer themes", "confirmed", None, "crossref_index.json"),
    _e("LEARN-018-PHOTO-INDEX", "topic", "Map photos to components", "confirmed", None, "photo_index.json"),
    _e("LEARN-019-REGENERATE", "topic", "Regenerate ledger and run pytest", "confirmed", None, "generate_ledger.py"),
    _e("LEARN-020-BOUNDARY", "topic", "Document unknowns honestly", "confirmed", None, "OMISSIONS_AND_REMAINING.md"),
]
