"""Tests for run_phase_b and validate_captures scripts."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_run_phase_b_exits_without_captures():
    """run_phase_b must not crash when captures/ is empty."""
    result = _run("run_phase_b.py")
    assert result.returncode == 0, result.stderr
    assert "Ledger refreshed" in result.stdout or "Phase B captures ingested" in result.stdout


def test_validate_captures_missing_returns_1():
    result = _run("validate_captures.py")
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["ready_for_phase_b"] is False


def test_validate_captures_rejects_wrong_eeprom_size(synthetic_eeprom_capture):
    if not SYNTH.exists():
        pytest.skip("synthetic fixture missing")
    CAPTURE.write_bytes(b"\x00" * 100)
    result = _run("validate_captures.py")
    assert result.returncode in (2, 3)
    data = json.loads(result.stdout)
    eeprom = next(c for c in data["checks"] if c["name"] == "eeprom.bin")
    assert eeprom["ok"] is False


def test_print_proposals_runs():
    _run("propose_phase_b_upgrades.py")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "print_proposals.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "升级建议" in result.stdout
