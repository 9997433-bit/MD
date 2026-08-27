"""Tests for agent resume JSON."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_agent_resume_after_bundle():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_handoff_bundle.py")], cwd=ROOT, check=True)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "agent_resume.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["task"] == "resume_phase_b"
    assert data["identifiers"] == 237
    assert (ROOT / "manifests" / "pr_body_snapshot.md").exists()
