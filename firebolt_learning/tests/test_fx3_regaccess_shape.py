"""PIB config / reg-access shape checks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_regaccess_shape_pib_cfg():
    data = json.loads((ROOT / "manifests" / "fx3_regaccess_shape.json").read_text(encoding="utf-8"))
    block = data["pib_config_block"]
    assert block["base"].lower() == "0xe0011000"
    # Base address write target is observed; SDK names it only as reserved gap.
    assert block["store_count"] >= 10
    assert data["boundary"]["is_fpga_fabric_regmap"] is False
    assert data["boundary"]["fx3_regmap_status"] == "unknown"
    assert set(data["subsystem_tags"]["names"]) >= {"Op", "Fpga", "Fusion", "Trace"}


def test_regaccess_doc():
    text = (ROOT / "docs" / "FX3_REGACCESS_SHAPE.md").read_text(encoding="utf-8")
    assert "0xE0011000" in text
    assert "fabric" in text.lower() or "REGMAP" in text
