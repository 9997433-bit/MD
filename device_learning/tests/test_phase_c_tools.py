"""Tests for phase transition, validate_captures, and phase C tools."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"
TEMPLATE = ROOT / "phase_c" / "templates" / "experiment_log_template.json"


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_validate_captures_rejects_synthetic_eeprom(synthetic_eeprom_capture):
    result = _run("validate_captures.py")
    assert result.returncode == 3
    data = json.loads(result.stdout)
    assert data["synthetic_fixture_detected"] is True


def test_phase_transition_with_fake_real_eeprom():
    CAPTURE.write_bytes(b"\xff" * 8192)
    _run("ingest_phase_b.py")
    _run("detect_phase_transition.py")
    t = json.loads((ROOT / "manifests" / "phase_transition.json").read_text())
    assert t["recommended_phase"] in ("phase_b_in_progress", "phase_b_partial_complete")
    assert t["capture_flags"]["eeprom_observed"] is True


def test_experiment_log_validation_template_invalid():
    logs = ROOT / "phase_c" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    target = logs / "_test_template.json"
    shutil.copy(TEMPLATE, target)
    try:
        _run("validate_experiment_log.py")
        data = json.loads((ROOT / "manifests" / "experiment_validation.json").read_text())
        row = next(r for r in data["files"] if r["file"] == "_test_template.json")
        assert row["valid"] is False
    finally:
        if target.exists():
            target.unlink()
        _run("sync_phase_c_checklist.py")


def test_run_phase_c_exits_zero():
    result = _run("run_phase_c.py")
    assert result.returncode == 0
    assert (ROOT / "PHASE_C_READINESS.md").exists()
