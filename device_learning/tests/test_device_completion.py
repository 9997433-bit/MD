"""Test static completion verification."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_completion_status():
    data = json.loads((ROOT / "manifests" / "completion_status.json").read_text())
    assert data["static_phase_complete"] is True


def test_static_report():
    assert (ROOT / "STATIC_REPORT.md").exists()
    text = (ROOT / "STATIC_REPORT.md").read_text()
    assert "静态分析报告" in text


def test_phase_c_scaffold():
    assert (ROOT / "phase_c" / "README.md").exists()


def test_exp_catalog():
    ledger = json.loads((ROOT / "EvidenceLedger.json").read_text())
    assert len(ledger["catalogs"]["exp"]) >= 15
