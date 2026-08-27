#!/usr/bin/env python3
"""Build a single manifest summarizing all phase B capture artifacts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"
ANALYSIS = ROOT / "phase_b" / "analysis"
OUT = ROOT / "manifests" / "capture_manifest.json"

EXPECTED = [
    "phase_b/captures/eeprom.bin",
    "phase_b/captures/usb_enum.pcapng",
    "phase_b/captures/usb_session.pcapng",
    "phase_b/captures/protocol_log.json",
    "phase_b/analysis/firmware.bin",
    "phase_b/analysis/mcu_disasm.txt",
]


def load_json(rel: str) -> dict | None:
    path = ROOT / rel
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"error": "invalid_json"}
    return None


def main() -> None:
    artifacts = []
    for rel in EXPECTED:
        path = ROOT / rel
        row = {"path": rel, "exists": path.is_file()}
        if row["exists"]:
            row["size_bytes"] = path.stat().st_size
        artifacts.append(row)

    phase_b = load_json("manifests/phase_b_status.json") or {}
    eeprom = load_json("manifests/eeprom_meta.json") or {}
    usb = load_json("manifests/usb_capture_meta.json") or {}
    proto = load_json("manifests/protocol_log_meta.json") or {}
    fw = load_json("manifests/firmware_extract.json") or {}

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
        "present_count": sum(1 for a in artifacts if a["exists"]),
        "expected_count": len(EXPECTED),
        "flags": phase_b.get("flags", {}),
        "eeprom_status": eeprom.get("status"),
        "usb_capture_status": usb.get("status"),
        "protocol_log_status": proto.get("status"),
        "firmware_extract_status": fw.get("status"),
        "ready_for_deep_analysis": bool(
            phase_b.get("flags", {}).get("eeprom_present")
            and phase_b.get("flags", {}).get("usb_capture_present")
        ),
        "boundary": "Inventory only; status upgrades require ledger refresh",
    }
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"present_count": manifest["present_count"], "ready_for_deep_analysis": manifest["ready_for_deep_analysis"]}, indent=2))


if __name__ == "__main__":
    main()
