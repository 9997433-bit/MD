#!/usr/bin/env python3
"""Print one-line project status to stdout."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cov = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "manifests" / "evidence_summary.json").read_text(encoding="utf-8"))
    freeze = {}
    transition = {}
    freeze_path = ROOT / "manifests" / "static_freeze.json"
    if freeze_path.exists():
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    trans_path = ROOT / "manifests" / "phase_transition.json"
    if trans_path.exists():
        transition = json.loads(trans_path.read_text(encoding="utf-8"))
    b_chk = json.loads((ROOT / "phase_b" / "CHECKLIST.json").read_text(encoding="utf-8"))
    print(
        f"phase={summary.get('phase')} "
        f"ids={summary.get('identifiers')} "
        f"confirmed={cov.get('status_counts', {}).get('confirmed', 0)} "
        f"blocked={summary.get('blocked')} "
        f"idcode={summary.get('bitstream', {}).get('idcode')} "
        f"eeprom={summary.get('eeprom_status')} "
        f"frozen={freeze.get('static_phase_complete', '?')} "
        f"b_chk={b_chk.get('done_count', 0)}/{b_chk.get('total_count', 0)} "
        f"next={transition.get('recommended_phase', 'n/a')} "
        f"pass={summary.get('stop_conditions_pass')}"
    )


if __name__ == "__main__":
    main()
