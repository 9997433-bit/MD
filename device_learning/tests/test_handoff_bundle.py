"""Tests for handoff bundle builder."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_handoff_bundle():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_handoff_bundle.py")], cwd=ROOT, check=True)
    data = json.loads((ROOT / "manifests" / "handoff_bundle.json").read_text())
    assert "sections" in data
    assert data["sections"]["manifests_static_closure"] is not None
    assert "make intake" in data["resume_commands"]
