#!/usr/bin/env python3
"""Detect whether package phase should transition based on captures."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"
STATUS_PATH = ROOT / "manifests" / "phase_b_status.json"


def load_phase_b_flags() -> dict:
    if STATUS_PATH.exists():
        return json.loads(STATUS_PATH.read_text(encoding="utf-8")).get("flags", {})
    return {}


def main() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from eeprom_source import is_synthetic_dump  # noqa: E402

    eeprom_path = CAPTURES / "eeprom.bin"
    eeprom_bytes = eeprom_path.read_bytes() if eeprom_path.exists() else b""
    flags = {
        "eeprom_file": eeprom_path.exists(),
        "eeprom_observed": eeprom_path.exists() and bool(eeprom_bytes) and not is_synthetic_dump(eeprom_bytes),
        "eeprom_synthetic": eeprom_path.exists() and bool(eeprom_bytes) and is_synthetic_dump(eeprom_bytes),
        "usb_enum": (CAPTURES / "usb_enum.pcapng").exists(),
        "usb_session": (CAPTURES / "usb_session.pcapng").exists(),
        "any_pcap": any(CAPTURES.glob("*.pcapng")) if CAPTURES.exists() else False,
    }
    # Prefer ingest flags when available (post-ingest)
    ingest = load_phase_b_flags()
    if "eeprom_observed" in ingest:
        flags["eeprom_observed"] = bool(ingest.get("eeprom_observed"))

    current = "static_complete_pending_hardware"
    recommended = current
    warnings: list[str] = []

    if flags["eeprom_synthetic"] and not flags["eeprom_observed"]:
        warnings.append("eeprom.bin matches synthetic fixture SHA-256 — not counted as real capture")

    if flags["eeprom_observed"] or flags["any_pcap"]:
        recommended = "phase_b_in_progress"
    if flags["eeprom_observed"] and flags["any_pcap"]:
        recommended = "phase_b_partial_complete"

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_phase": current,
        "recommended_phase": recommended,
        "transition_ready": recommended != current,
        "capture_flags": flags,
        "warnings": warnings,
        "action": (
            "make phase-b"
            if flags["eeprom_observed"] or flags["any_pcap"]
            else "place real captures in phase_b/captures/ (see HARDWARE_HANDOFF.md)"
        ),
    }
    out = ROOT / "manifests" / "phase_transition.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"recommended_phase": recommended, "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
