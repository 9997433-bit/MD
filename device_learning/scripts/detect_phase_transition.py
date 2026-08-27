#!/usr/bin/env python3
"""Detect whether package phase should transition based on captures."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"


def main() -> None:
    flags = {
        "eeprom": (CAPTURES / "eeprom.bin").exists(),
        "usb_enum": (CAPTURES / "usb_enum.pcapng").exists(),
        "usb_session": (CAPTURES / "usb_session.pcapng").exists(),
        "any_pcap": any(CAPTURES.glob("*.pcapng")) if CAPTURES.exists() else False,
    }
    current = "static_complete_pending_hardware"
    recommended = current
    if flags["eeprom"] or flags["any_pcap"]:
        recommended = "phase_b_in_progress"
    if flags["eeprom"] and flags["any_pcap"]:
        recommended = "phase_b_partial_complete"

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_phase": current,
        "recommended_phase": recommended,
        "transition_ready": recommended != current,
        "capture_flags": flags,
        "action": "make phase-b" if flags["eeprom"] or flags["any_pcap"] else "place files in phase_b/captures/",
    }
    out = ROOT / "manifests" / "phase_transition.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"recommended_phase": recommended}, indent=2))


if __name__ == "__main__":
    main()
