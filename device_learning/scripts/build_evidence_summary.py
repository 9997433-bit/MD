#!/usr/bin/env python3
"""Build a one-page evidence summary for quick review."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _idcode(frame: dict) -> str | None:
    reg = frame.get("packet_stream", {}).get("registers", {}).get("IDCODE", {})
    return reg.get("raw") or frame.get("idcode", {}).get("raw")


def main() -> None:
    cov = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    pending = json.loads((ROOT / "manifests" / "pending_index.json").read_text(encoding="utf-8"))
    phase_b = json.loads((ROOT / "manifests" / "phase_b_status.json").read_text(encoding="utf-8"))
    frame = json.loads((ROOT / "manifests" / "frame_summary.json").read_text(encoding="utf-8"))
    eeprom = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text(encoding="utf-8"))
    integrity = json.loads((ROOT / "manifests" / "catalog_integrity.json").read_text(encoding="utf-8"))

    fa = frame.get("frame_analysis", {})
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": cov.get("phase"),
        "identifiers": cov.get("total_identifiers"),
        "status_counts": cov.get("status_counts"),
        "blocked": pending.get("total_blocked"),
        "hardware_ready": phase_b.get("flags", {}),
        "bitstream": {
            "idcode": _idcode(frame),
            "part": frame.get("bit_container", {}).get("sections", {}).get("b_part_name", {}).get("value"),
            "build_date": frame.get("bit_container", {}).get("sections", {}).get("c_date", {}).get("value"),
            "frames_est": fa.get("estimated_frame_count"),
            "iob_candidate": fa.get("candidate_iob_config_words"),
        },
        "eeprom_status": eeprom.get("status"),
        "catalog_integrity_ok": integrity.get("ok"),
        "stop_conditions_pass": cov.get("all_pass"),
        "declaration": cov.get("declaration"),
    }
    out = ROOT / "manifests" / "evidence_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
