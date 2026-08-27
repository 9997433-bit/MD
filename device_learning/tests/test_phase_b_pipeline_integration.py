"""Integration test: phase B pipeline with synthetic EEPROM (not device data)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"


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
    assert transition["recommended_phase"] == "static_complete_pending_hardware"
    assert transition["capture_flags"]["eeprom_synthetic"] is True
    assert transition["capture_flags"]["eeprom_observed"] is False

    checklist = json.loads((ROOT / "phase_b" / "CHECKLIST.json").read_text())
    b1 = next(t for t in checklist["tasks"] if t["id"] == "B1")
    assert b1["done"] is True


def test_no_real_eeprom_committed():
    """Captures dir must not contain real dump in static-only repo state."""
    if CAPTURE.exists():
        meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
        assert meta.get("status") != "observed", "real eeprom.bin should not be committed without capture"
