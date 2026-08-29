"""Firmware / bitstream manifest checks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_firmware_files_present():
    assert (ROOT / "firmware" / "niusbFirebolt.cfg").is_file()
    assert (ROOT / "firmware" / "niusbFireboltFPGA.cfg").is_file()


def test_firmware_meta_vid_pid():
    meta = json.loads((ROOT / "manifests" / "firmware_meta.json").read_text(encoding="utf-8"))
    assert meta["cy_header"] is True
    assert meta["idVendor"] == 0x3923
    assert meta["idProduct"] == 0x7B44
    anchors = "\n".join(meta.get("anchor_strings", []))
    assert "nimarengo" in anchors
    assert "Fusion" in anchors
    assert "tFPGA" in anchors or "FPGA" in anchors


def test_bitstream_idcode():
    meta = json.loads((ROOT / "manifests" / "bitstream_meta.json").read_text(encoding="utf-8"))
    assert meta["idcode"] == "0x0362C093"
    assert meta["idcode_device"] == "XC7A100T"
    assert meta["sync_offset"] is not None and meta["sync_offset"] >= 0


def test_file_hashes_stable():
    hashes = json.loads((ROOT / "manifests" / "file_hashes.json").read_text(encoding="utf-8"))
    assert hashes["firmware/niusbFirebolt.cfg"].startswith("6d0aa09e")
    assert hashes["firmware/niusbFireboltFPGA.cfg"].startswith("cc5c15f4")


def test_system_map_nodes():
    sm = json.loads((ROOT / "manifests" / "system_map.json").read_text(encoding="utf-8"))
    ids = {n["id"] for n in sm["nodes"]}
    assert ids >= {
        "NODE-AI-IN",
        "NODE-ADC16",
        "NODE-FPGA",
        "NODE-FX3",
        "NODE-USB",
        "NODE-HOST",
    }
    host = next(n for n in sm["nodes"] if n["id"] == "NODE-HOST")
    assert host["status"] == "not_started"


def test_photo_index_remote_policy():
    idx = json.loads((ROOT / "manifests" / "photo_index.json").read_text(encoding="utf-8"))
    assert idx["count"] == 17
    assert "not vendored" in idx["policy"]
    assert idx["source_repo"].endswith("Montyzhang/sixfour")
