"""Smoke test for PR body generator."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_print_pr_body():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "print_pr_body.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "237" in result.stdout
    assert "make intake" in result.stdout
