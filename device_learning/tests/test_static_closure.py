"""Tests for static closure report."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_static_closure():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_static_closure.py")], cwd=ROOT, check=True)
    data = json.loads((ROOT / "manifests" / "static_closure.json").read_text())
    assert data["static_phase_closed"] is True
    assert data["identifiers"] == 237
    assert (ROOT / "STATIC_CLOSURE.md").exists()
