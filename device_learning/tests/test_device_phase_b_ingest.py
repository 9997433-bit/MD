"""Tests for phase B ingest and USB capture stub."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase_b_status_manifest():
    path = ROOT / "manifests" / "phase_b_status.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert "flags" in data
    assert data["flags"]["eeprom_present"] is False


def test_usb_capture_meta_missing_ok():
    path = ROOT / "manifests" / "usb_capture_meta.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["status"] in ("missing", "observed")


def test_bit_strings_manifest():
    path = ROOT / "manifests" / "bit_strings.json"
    assert path.exists()
    text = path.read_text().lower()
    assert "4431" not in text
    assert "topusb" not in text
    data = json.loads(text)
    assert data.get("unique_redacted_count", 0) > 0


def test_hardware_handoff_exists():
    assert (ROOT / "HARDWARE_HANDOFF.md").exists()
