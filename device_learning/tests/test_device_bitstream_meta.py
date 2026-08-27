"""Test bitstream metadata fields."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bitstream_meta_exists():
    assert (ROOT / "manifests" / "bitstream_meta.json").exists()


def test_bitstream_meta_fields():
    meta = json.loads((ROOT / "manifests" / "bitstream_meta.json").read_text())
    header = meta.get("header", meta)
    blob = json.dumps(header).lower()
    assert "3s200" in blob


def test_frame_summary_exists():
    assert (ROOT / "manifests" / "frame_summary.json").exists()


def test_frame_summary_fields():
    summary = json.loads((ROOT / "manifests" / "frame_summary.json").read_text())
    if "frame_scan" in summary:
        assert summary["frame_scan"]["word_count"] > 0
    else:
        assert summary.get("parse_status") or summary.get("frame_analysis")
