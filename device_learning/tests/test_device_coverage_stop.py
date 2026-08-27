"""Test coverage stop conditions."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_coverage_exists():
    cov = ROOT / "coverage.json"
    assert cov.exists(), "Run generate_ledger.py first"


def test_stop_conditions():
    cov = json.loads((ROOT / "coverage.json").read_text())
    stop = cov["stop_conditions"]
    assert stop["1_no_empty_status"] is True
    assert stop["2_all_layers_present"] is True
    assert stop["4_null_bridges_intact"] is True


def test_total_identifiers():
    cov = json.loads((ROOT / "coverage.json").read_text())
    assert cov["total_identifiers"] >= 230
    assert cov.get("phase") == "static_complete_pending_hardware"
    assert cov["stop_conditions"].get("7_learning_guide") is True
