"""PIB/GPIF MMIO map checks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fx3_mmio_pib_stride():
    data = json.loads((ROOT / "manifests" / "fx3_mmio_map.json").read_text(encoding="utf-8"))
    stride = data["pib_socket_stride"]
    assert stride["status"] == "confirmed"
    assert "0xE0010000" in stride["pattern"]
    assert any("lsl" in x for x in stride["insns"])
    assert any("0x10000" in x for x in stride["insns"])
    joined = " ".join(stride.get("decoded_at_va") or [])
    assert "lsl" in joined and ("0xe0000000" in joined.lower() or "e0000000" in joined.lower())
    assert data["region_literal_hits"].get("PIB_GPIF", 0) >= 1
    assert data["region_literal_hits"].get("UIB_USB", 0) >= 1


def test_gpif_doc_exists():
    text = (ROOT / "docs" / "FX3_GPIF_PATH.md").read_text(encoding="utf-8")
    assert "0xE0010000" in text
    assert "socket" in text.lower()
