"""Smoke test for make help."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_make_help():
    result = subprocess.run(["make", "help"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert "make intake" in result.stdout
    assert "make finalize" in result.stdout
