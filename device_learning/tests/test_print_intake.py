"""Smoke test for intake guide script."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_print_intake_runs():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "print_intake.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "实机接入向导" in result.stdout
    assert "eeprom.bin" in result.stdout
