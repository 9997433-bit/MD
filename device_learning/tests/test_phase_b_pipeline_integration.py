"""Integration test: phase B pipeline with synthetic EEPROM (not device data)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"


@pytest.fixture
def synthetic_eeprom_capture():
    """Temporarily place synthetic fixture in captures/; always cleaned up."""
    CAPTURE.parent.mkdir(parents=True, exist_ok=True)
    backup = CAPTURE.read_bytes() if CAPTURE.exists() else None
    shutil.copy(SYNTH, CAPTURE)
    yield
    if backup is not None:
        CAPTURE.write_bytes(backup)
    elif CAPTURE.exists():
        CAPTURE.unlink()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "ingest_phase_b.py")], cwd=ROOT, check=False)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_phase_b_checklist.py")], cwd=ROOT, check=False)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "detect_phase_transition.py")], cwd=ROOT, check=False)


def _run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def test_phase_b_pipeline_synthetic(synthetic_eeprom_capture):
    _run("ingest_phase_b.py")
    _run("analyze_eeprom.py")
    _run("scan_firmware_stub.py")
    _run("detect_phase_transition.py")
    _run("sync_phase_b_checklist.py")

    meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
    assert meta["status"] in ("synthetic_pipeline_test", "observed")
    assert meta.get("boot_format") == "C2"

    transition = json.loads((ROOT / "manifests" / "phase_transition.json").read_text())
    assert transition["recommended_phase"] == "phase_b_in_progress"
    assert transition["capture_flags"]["eeprom"] is True

    checklist = json.loads((ROOT / "phase_b" / "CHECKLIST.json").read_text())
    b1 = next(t for t in checklist["tasks"] if t["id"] == "B1")
    assert b1["done"] is True


def test_no_real_eeprom_committed():
    """Captures dir must not contain real dump in static-only repo state."""
    if CAPTURE.exists():
        meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
        assert meta.get("status") != "observed", "real eeprom.bin should not be committed without capture"
