"""Tests for confirmed report, photo map, and status CLI."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_confirmed_report():
    path = ROOT / "CONFIRMED_REPORT.md"
    assert path.exists()
    text = path.read_text()
    assert "HW-001-FPGA-DEVICE" in text
    assert "confirmed 总数" in text or "confirmed" in text.lower()


def test_photo_hw_map():
    data = json.loads((ROOT / "manifests" / "photo_hw_map.json").read_text())
    assert data["photo_count"] == 10
    assert data["photos_with_hw_links"] >= 5


def test_print_status_cli():
    out = subprocess.check_output(["python3", "scripts/print_status.py"], cwd=ROOT, text=True)
    assert "idcode=0x01414093" in out
    assert "frozen=True" in out
    assert "phase=" in out
    assert "ids=237" in out
