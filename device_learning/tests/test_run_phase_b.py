"""Tests for run_phase_b and validate_captures scripts."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


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
    captures = ROOT / "phase_b" / "captures"
    backup = list(captures.iterdir()) if captures.exists() else []
    for p in backup:
        if p.is_file():
            p.unlink()
    try:
        result = _run("validate_captures.py")
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["ready_for_phase_b"] is False
    finally:
        subprocess.run([sys.executable, str(SCRIPTS / "ingest_phase_b.py")], cwd=ROOT, check=False)


def test_validate_captures_rejects_wrong_eeprom_size(tmp_path):
    synth = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
    if not synth.exists():
        pytest.skip("synthetic fixture missing")
    captures = ROOT / "phase_b" / "captures"
    captures.mkdir(parents=True, exist_ok=True)
    bad = captures / "eeprom.bin"
    backup = bad.read_bytes() if bad.exists() else None
    bad.write_bytes(b"\x00" * 100)
    try:
        result = _run("validate_captures.py")
        assert result.returncode == 2
        data = json.loads(result.stdout)
        eeprom = next(c for c in data["checks"] if c["name"] == "eeprom.bin")
        assert eeprom["ok"] is False
    finally:
        if backup is not None:
            bad.write_bytes(backup)
        elif bad.exists():
            bad.unlink()
