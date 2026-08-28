"""Coverage stop-condition checks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_coverage_stop_not_vendor_eq():
    c = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    sc = c["stop_condition"]
    assert sc["catalog_complete"] is True
    assert sc["vendor_equivalent"] is False
    assert sc["runtime_behavior_mastered"] is False
    assert sc["usb_capture_done"] is False
    assert c["forced_null_bridge_count"] >= 8
