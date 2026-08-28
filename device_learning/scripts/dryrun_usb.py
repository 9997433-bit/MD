#!/usr/bin/env python3
"""Dry-run USB capture ingest using synthetic pcapng (NOT device data).

Isolates captures/: real Phase B artifacts are stashed so the synthetic-only
path can prove that fixture SHA is not counted as observed.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "phase_b" / "fixtures" / "usb_enum_synthetic_reference.pcapng"
CAPTURES = ROOT / "phase_b" / "captures"
CAPTURE = CAPTURES / "usb_enum.pcapng"
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / name)], cwd=ROOT, check=True)


def main() -> int:
    if not SYNTH.exists():
        subprocess.run([sys.executable, str(SCRIPTS / "build_pcap_synthetic.py")], cwd=ROOT, check=True)

    CAPTURES.mkdir(parents=True, exist_ok=True)
    stash = Path(tempfile.mkdtemp(prefix="dryrun_usb_stash_"))
    stashed: list[str] = []
    try:
        for path in list(CAPTURES.iterdir()):
            if path.is_file() and path.name != ".gitkeep":
                shutil.move(str(path), str(stash / path.name))
                stashed.append(path.name)

        shutil.copy(SYNTH, CAPTURE)
        print("WARNING: using synthetic pcapng in captures/ — NOT device data")
        for s in (
            "ingest_phase_b.py",
            "analyze_pcap_stub.py",
            "detect_phase_transition.py",
            "sync_phase_b_checklist.py",
        ):
            run(s)
        transition = __import__("json").loads((ROOT / "manifests" / "phase_transition.json").read_text())
        assert transition["recommended_phase"] == "static_complete_pending_hardware", transition
        print("Dry-run USB complete (synthetic not counted as observed).")
        return 0
    finally:
        if CAPTURE.exists():
            CAPTURE.unlink()
        for name in stashed:
            src = stash / name
            if src.exists():
                shutil.move(str(src), str(CAPTURES / name))
        shutil.rmtree(stash, ignore_errors=True)
        (CAPTURES / ".gitkeep").touch(exist_ok=True)
        run("sync_phase_b_checklist.py")
        run("detect_phase_transition.py")


if __name__ == "__main__":
    sys.exit(main())
