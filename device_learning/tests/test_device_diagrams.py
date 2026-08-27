"""Tests for architecture diagram, bridge report, and artifact inventory."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_architecture_mermaid():
    text = (ROOT / "ARCHITECTURE.md").read_text()
    assert "flowchart LR" in text
    assert "NODE-FPGA" in text


def test_bridge_report():
    text = (ROOT / "BRIDGE_REPORT.md").read_text()
    assert "null" in text
    assert "bitstream_frame" in text


def test_artifact_inventory():
    data = json.loads((ROOT / "manifests" / "artifact_inventory.json").read_text())
    assert data["present_count"] >= 18


def test_static_report_idcode():
    text = (ROOT / "STATIC_REPORT.md").read_text()
    assert "0x01414093" in text
