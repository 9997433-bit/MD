"""Assert USB protocol decode against enum capture when available."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ENUM = ROOT / "phase_b" / "captures" / "usb_enum.pcapng"
DECODE = ROOT / "manifests" / "usb_protocol_decode.json"


@pytest.mark.skipif(not ENUM.exists(), reason="phase_b/captures/usb_enum.pcapng missing")
def test_usb_protocol_decode_primary_bulk():
    if not DECODE.exists():
        return
    data = json.loads(DECODE.read_text())
    if data.get("status") != "decoded":
        return
    assert data["primary_device"]["idVendor"] == "0x3923"
    assert data["primary_device"]["idProduct"] == "0x744f"
    assert len(data["endpoints"]) == 4
    assert data["transfer_mode"]["mode"] == "bulk"
