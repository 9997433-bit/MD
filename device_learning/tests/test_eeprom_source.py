"""Tests for EEPROM source detection and phase B upgrade proposals."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_analyze_eeprom_marks_synthetic_in_captures(synthetic_eeprom_capture):
    _run("analyze_eeprom.py")
    meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
    assert meta["status"] == "synthetic_pipeline_test"
    assert "warning" in meta


def test_ingest_flags_synthetic_eeprom(synthetic_eeprom_capture):
    _run("ingest_phase_b.py")
    status = json.loads((ROOT / "manifests" / "phase_b_status.json").read_text())
    assert status["flags"]["eeprom_present"] is True
    assert status["flags"]["eeprom_observed"] is False
    assert status["ready_for_ledger_refresh"] is False


def test_propose_upgrades_empty_without_real_capture():
    _run("propose_phase_b_upgrades.py")
    data = json.loads((ROOT / "manifests" / "phase_b_upgrade_proposals.json").read_text())
    assert data["proposal_count"] == 0


def test_build_phase_b_readiness():
    _run("build_phase_b_readiness.py")
    assert (ROOT / "PHASE_B_READINESS.md").exists()
    data = json.loads((ROOT / "manifests" / "phase_b_readiness.json").read_text())
    assert data["blocker_count"] >= 3
