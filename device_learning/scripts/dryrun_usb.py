#!/usr/bin/env python3
"""Dry-run USB capture ingest using synthetic pcapng (NOT device data)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "phase_b" / "fixtures" / "usb_enum_synthetic_reference.pcapng"
CAPTURE = ROOT / "phase_b" / "captures" / "usb_enum.pcapng"
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / name)], cwd=ROOT, check=True)


def main() -> int:
    if not SYNTH.exists():
        subprocess.run([sys.executable, str(SCRIPTS / "build_pcap_synthetic.py")], cwd=ROOT, check=True)
    backup = CAPTURE.read_bytes() if CAPTURE.exists() else None
    CAPTURE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SYNTH, CAPTURE)
    print("WARNING: using synthetic pcapng in captures/ — NOT device data")
    try:
        for s in (
            "ingest_phase_b.py",
            "analyze_pcap_stub.py",
            "detect_phase_transition.py",
            "sync_phase_b_checklist.py",
        ):
            run(s)
        transition = __import__("json").loads((ROOT / "manifests" / "phase_transition.json").read_text())
        assert transition["recommended_phase"] == "static_complete_pending_hardware"
        print("Dry-run USB complete (synthetic not counted as observed).")
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
