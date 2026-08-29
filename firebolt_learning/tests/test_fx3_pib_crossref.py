"""Cypress PIB/GPIF cross-reference checks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pib_crossref_core_hits():
    data = json.loads((ROOT / "manifests" / "fx3_pib_crossref.json").read_text(encoding="utf-8"))
    by_addr = {h["address"].lower(): h for h in data["named_literal_hits"]}
    assert by_addr["0xe0010000"]["present"] is True
    assert by_addr["0xe0014000"]["present"] is True
    assert by_addr["0xe0018000"]["present"] is True
    assert data["official_layout_summary"]["socket_stride_bytes"] == 128
    assert data["pp_mmio_path"]["status"] == "unknown"
    assert data["e0011000_clarification"]["status"] == "candidate"


def test_crossref_doc():
    text = (ROOT / "docs" / "FX3_PIB_CROSSREF.md").read_text(encoding="utf-8")
    assert "0xE0014000" in text and "0x80" in text
