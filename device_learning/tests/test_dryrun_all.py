"""Test combined dryrun-all target."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dryrun_all():
    result = subprocess.run(["make", "dryrun-all"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "Both synthetic dry-runs complete" in result.stdout
