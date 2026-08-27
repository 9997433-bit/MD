#!/usr/bin/env python3
"""Dry-run phase B pipeline using synthetic EEPROM (NOT device data).

Proves ingest → analyze → transition detection works before real hardware.
Always removes synthetic copy from captures/ on exit.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / name)], cwd=ROOT, check=True)


def main() -> int:
    if not SYNTH.exists():
        print("Missing synthetic fixture; run make ledger first.", file=sys.stderr)
        return 1
    backup = CAPTURE.read_bytes() if CAPTURE.exists() else None
    CAPTURE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SYNTH, CAPTURE)
    print("WARNING: using synthetic fixture in captures/ — NOT device data")
    try:
        for s in (
            "ingest_phase_b.py",
            "analyze_eeprom.py",
            "scan_firmware_stub.py",
            "detect_phase_transition.py",
            "sync_phase_b_checklist.py",
            "build_checklist_report.py",
        ):
            run(s)
        print("Dry-run complete. Review manifests/phase_transition.json and phase_b/CHECKLIST.json")
        return 0
    finally:
        if backup is not None:
            CAPTURE.write_bytes(backup)
        elif CAPTURE.exists():
            CAPTURE.unlink()
        run("sync_phase_b_checklist.py")
        run("detect_phase_transition.py")


if __name__ == "__main__":
    sys.exit(main())
