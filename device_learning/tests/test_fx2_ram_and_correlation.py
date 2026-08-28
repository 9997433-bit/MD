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
def test_fx2_ivt_and_1435():
    ivt = ROOT / "manifests" / "fx2_ivt_map.json"
    ann = ROOT / "manifests" / "fx2_routine_1435_annotation.json"
    if ivt.exists():
        data = json.loads(ivt.read_text(encoding="utf-8"))
        if data.get("status") == "scanned":
            assert data["vectors"][0]["ljmp_dest"] == "0x075b"
    if ann.exists():
        data = json.loads(ann.read_text(encoding="utf-8"))
        if data.get("status") == "annotated":
            assert data["routine_entry"] == "0x1435"
            assert any(s["label"] == "EP6CS" for s in data.get("sfr_access_sequence") or [])


@pytest.mark.skipif(not RAM.exists(), reason="fx2_ram_from_enum.bin missing")
def test_fx2_stream_path_manifest():
    path = ROOT / "manifests" / "fx2_stream_path.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "stream_path_scanned":
        return
    assert data["hub_entry"] == "0x1435"
    assert data.get("confidence") == "candidate"
    assert data.get("semantics") == "unknown"
    assert isinstance(data.get("arm_stream_micro_ops_ordered"), list)
    assert len(data.get("arm_stream_micro_ops_ordered") or []) >= 1
    compact = data.get("arm_stream_compact_candidates") or []
    assert isinstance(compact, list)
    assert any(a.get("label") == "EP6CS" for a in compact) or any(
        a.get("label") == "EP6CS" for a in (data.get("arm_stream_micro_ops_ordered") or [])
    )
    assert "0x1435" in (data.get("seed_entries") or [])
    graph = data.get("call_jump_graph") or {}
    assert graph.get("edge_count", 0) >= 1
    # Forbidden product digit string must never appear in this artifact
    blob = path.read_text(encoding="utf-8")
    assert "44" + "31" not in blob
    notes = ROOT / "phase_b" / "analysis" / "MCU_NOTES.md"
    if notes.exists():
        assert "Stream path walk" in notes.read_text(encoding="utf-8")
        assert "44" + "31" not in notes.read_text(encoding="utf-8")


@pytest.mark.skipif(not RAM.exists(), reason="fx2_ram_from_enum.bin missing")
def test_fx2_address_map_and_init_chain():
    amap = ROOT / "manifests" / "fx2_address_map.json"
    init = ROOT / "manifests" / "fx2_init_chain.json"
    if amap.exists():
        data = json.loads(amap.read_text(encoding="utf-8"))
        if data.get("status") == "mapped":
            assert data["size_bytes"] == 16384
            reset = data.get("reset") or {}
            assert reset.get("target") == "0x075b"
            assert any(a.get("start") == "0x1435" for a in data.get("anchors") or [])
    if init.exists():
        data = json.loads(init.read_text(encoding="utf-8"))
        if data.get("status") == "scanned":
            assert data["reset_target"] == "0x075b"
            assert isinstance(data.get("movx_write_label_first_seen_order"), list)
            assert len(data.get("movx_write_label_first_seen_order") or []) >= 1
            assert any(c.get("dest") == "0x1435" for c in data.get("highlight_calls_to_0x1435") or [])
