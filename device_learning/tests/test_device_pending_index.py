"""Tests for pending index and phase B runner."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pending_index_exists():
    path = ROOT / "manifests" / "pending_index.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["total_blocked"] >= 90
    assert "by_layer" in data
    assert "missing" in data["by_status"]


def test_pending_index_usb_missing():
    data = json.loads((ROOT / "manifests" / "pending_index.json").read_text())
    usb_blocked = data["by_layer"].get("usb", {}).get("count", 0)
    assert usb_blocked >= 10


def test_run_phase_b_script_exists():
    assert (ROOT / "scripts" / "run_phase_b.py").exists()
