#!/usr/bin/env python3
"""Build phase B/C roadmap: which actions unblock which identifiers."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_exp import ENTRIES as EXP
from catalogs.catalog_usb import ENTRIES as USB

PHASE_B_ACTIONS = [
    {
        "action": "eeprom_dump",
        "artifact": "phase_b/captures/eeprom.bin",
        "unblocks": [
            e["identifier"]
            for e in USB
            if e["status"] == "missing" and e.get("module") in ("mcu", "eeprom")
        ],
        "feeds": ["analyze_eeprom.py", "scan_firmware_stub.py", "EXP-010-8051-DISASM", "EXP-012-VIDPID"],
    },
    {
        "action": "usb_enum_capture",
        "artifact": "phase_b/captures/usb_enum.pcapng",
        "unblocks": [e["identifier"] for e in USB if e["layer"] == "PROTO" and e["status"] in ("not_started", "unknown")][:5],
        "feeds": ["analyze_pcap_stub.py", "EXP-002-USB-ENUM", "EXP-013-ENDPOINT-MAP"],
    },
    {
        "action": "usb_session_capture",
        "artifact": "phase_b/captures/usb_session.pcapng",
        "unblocks": ["EXP-003-USB-SESSION", "EXP-011-PROTO-TABLE", "EXP-014-DATA-FRAME"],
        "feeds": ["analyze_pcap_stub.py"],
    },
]

PHASE_C_ACTIONS = [
    {"experiment": e["identifier"], "description": e["description"], "status": e["status"], "depends": e.get("boundary")}
    for e in EXP
]


def main() -> None:
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase_b": PHASE_B_ACTIONS,
        "phase_c": PHASE_C_ACTIONS,
        "note": "Roadmap only; status upgrades require real evidence in ledger refresh",
    }
    out = ROOT / "manifests" / "phase_roadmap.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"phase_b_actions": len(PHASE_B_ACTIONS), "phase_c_experiments": len(PHASE_C_ACTIONS)}, indent=2))


if __name__ == "__main__":
    main()
