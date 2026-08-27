"""Test system map and architecture layer."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_system_map():
    p = ROOT / "manifests" / "system_map.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["node_count"] >= 6
    assert data["edge_count"] >= 5


def test_eeprom_meta_missing():
    meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
    assert meta["status"] == "missing"


def test_eeprom_layout_ref():
    layout = json.loads((ROOT / "manifests" / "eeprom_layout_ref.json").read_text())
    assert len(layout["fields"]) >= 8


def test_bit_confirmed_in_ledger():
    ledger = json.loads((ROOT / "EvidenceLedger.json").read_text())
    ids = {e["identifier"] for e in ledger["catalogs"]["bit"]}
    for req in ("BIT-IDCODE", "BIT-SYNC-WORD", "BIT-FLR", "BIT-CMD-SEQUENCE"):
        assert req in ids
