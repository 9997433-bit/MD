"""Tests for package manifest and handoff printer."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_package_manifest():
    data = json.loads((ROOT / "manifests" / "package_manifest.json").read_text())
    assert data["version"] == "static-1.0"
    assert data["static_phase_complete"] is True
    assert data["metrics"]["identifiers"] >= 237
    assert data["metrics"]["pytest_count"] >= 74


def test_print_handoff():
    out = subprocess.check_output(["python3", "scripts/print_handoff.py"], cwd=ROOT, text=True)
    assert "eeprom.bin" in out
    assert "make phase-b" in out
