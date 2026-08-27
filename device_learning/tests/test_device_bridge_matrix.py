"""Test forced null bridges are intact."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_null_bridge_count():
    data = json.loads((ROOT / "bridge_matrix.json").read_text())
    assert len(data["forced_null_bridges"]) >= 8


def test_all_bridges_null():
    data = json.loads((ROOT / "bridge_matrix.json").read_text())
    for entry in data["entries"]:
        assert entry["status"] is None, f"Bridge {entry['bridge']} was upgraded"
