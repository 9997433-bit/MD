"""USB descriptor static RE checks (no capture)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fx3_static_re_usb_topology():
    path = ROOT / "manifests" / "fx3_static_re.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    usb = data["usb_descriptors"]
    assert usb["device"]["idVendor"] == "0x3923"
    assert usb["device"]["idProduct"] == "0x7b44"
    assert len(usb["interfaces"]) >= 1
    assert usb["interfaces"][0]["bInterfaceClass"] == 255
    assert len(usb["endpoints"]) == 16
    assert data["bulk_endpoint_count"] == 15
    assert data["load_base_heuristic"].lower() == "0x3ffd6000"


def test_data_path_doc_exists():
    text = (ROOT / "docs" / "DATA_PATH.md").read_text(encoding="utf-8")
    assert "Signal Stream" in text
    assert "vendor" in text.lower()
    assert "8191" in text
