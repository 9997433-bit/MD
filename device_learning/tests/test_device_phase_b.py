"""Test deep frame scan manifest."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_frame_deep_exists():
    assert (ROOT / "manifests" / "frame_deep.json").exists()


def test_frame_deep_scan():
    data = json.loads((ROOT / "manifests" / "frame_deep.json").read_text())
    if "scan" in data:
        assert data["scan"]["word_count"] > 60000
    elif "frame_type_counts" in data:
        assert data["frame_type_counts"]["estimated_frame_count"] >= 600
    else:
        frames = data.get("frames", {})
        assert frames.get("estimated_frame_count", 0) >= 600


def test_phase_b_scaffold():
    assert (ROOT / "phase_b" / "README.md").exists()
    assert (ROOT / "phase_b" / "templates" / "eeprom_read.md").exists()
