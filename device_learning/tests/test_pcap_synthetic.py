"""Tests for synthetic USB pcap fixture."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SYNTH = ROOT / "phase_b" / "fixtures" / "usb_enum_synthetic_reference.pcapng"
CAPTURE = ROOT / "phase_b" / "captures" / "usb_enum.pcapng"


def test_build_pcap_synthetic():
    subprocess.run([sys.executable, str(SCRIPTS / "build_pcap_synthetic.py")], cwd=ROOT, check=True)
    assert SYNTH.exists()
    meta = json.loads((ROOT / "manifests" / "pcap_synthetic_meta.json").read_text())
    assert meta["magic"] == "pcapng"


def test_dryrun_usb_synthetic_not_observed():
    subprocess.run([sys.executable, str(SCRIPTS / "build_pcap_synthetic.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(SCRIPTS / "dryrun_usb.py")], cwd=ROOT, check=True)
    status = json.loads((ROOT / "manifests" / "phase_b_status.json").read_text())
    assert status["flags"].get("usb_capture_observed") is False


def test_validate_captures_rejects_synthetic_pcap():
    subprocess.run([sys.executable, str(SCRIPTS / "build_pcap_synthetic.py")], cwd=ROOT, check=True)
    CAPTURE.parent.mkdir(parents=True, exist_ok=True)
    backup = CAPTURE.read_bytes() if CAPTURE.exists() else None
    shutil.copy(SYNTH, CAPTURE)
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_captures.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 3
    finally:
        if backup is not None:
            CAPTURE.write_bytes(backup)
        elif CAPTURE.exists():
            CAPTURE.unlink()
