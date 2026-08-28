"""Tests for FX2 RAM scan and cmd/data correlation manifests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"


@pytest.mark.skipif(not RAM.exists(), reason="fx2_ram_from_enum.bin missing")
def test_fx2_ram_scan_manifest():
    scan = ROOT / "manifests" / "fx2_ram_scan.json"
    if not scan.exists():
        return
    data = json.loads(scan.read_text(encoding="utf-8"))
    if data.get("status") != "scanned":
        return
    assert data["size_bytes"] == 16384
    assert "reset_vector_hint" in data
    assert "NOT eeprom" in data.get("source_note", "") or "NOT eeprom" in data.get("boundary", "")


@pytest.mark.skipif(not RAM.exists(), reason="fx2_ram_from_enum.bin missing")
def test_fx2_ram_xrefs_manifest():
    path = ROOT / "manifests" / "fx2_ram_xrefs.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "scanned":
        return
    assert data["abs_branch_count"] >= 1
    assert data["vectors"][0]["vector"] == "reset"
    assert "NOT eeprom" in data.get("source_note", "")


@pytest.mark.skipif(not SESSION.exists(), reason="usb_session.pcapng missing")
def test_cmd_data_correlation_manifest():
    path = ROOT / "manifests" / "usb_cmd_data_correlation.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "hypothesis":
        return
    assert data["ep84_burst_count"] >= 1
    assert data["ep01_out_count"] >= 1


@pytest.mark.skipif(not RAM.exists(), reason="fx2_ram_from_enum.bin missing")
def test_fx2_l3_l5_manifests():
    for name, status_key in (
        ("fx2_ram_routines.json", "scanned"),
        ("fx2_cmd_dispatch_hypothesis.json", "hypothesis"),
        ("fx2_datapath_hypothesis.json", "hypothesis"),
    ):
        path = ROOT / "manifests" / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status") != status_key:
            continue
        assert "declaration" in data
        if name == "fx2_ram_routines.json":
            assert data["routine_count"] >= 1
        if name == "fx2_cmd_dispatch_hypothesis.json":
            assert data["dispatch_candidates"]
        if name == "fx2_datapath_hypothesis.json":
            assert data["datapath_routine_candidates"] is not None
