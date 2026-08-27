"""Test bitstream metadata fields."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_bitstream_meta_exists():
    meta_path = ROOT / "manifests" / "bitstream_meta.json"
    assert meta_path.exists(), "Run parse_bit_header.py first"


def test_bitstream_meta_fields():
    meta = json.loads((ROOT / "manifests" / "bitstream_meta.json").read_text())
    header = meta.get("header", meta)
    part = header.get("part_name") or header.get("device", "")
    assert "3s200" in str(part).lower() or "3s200" in json.dumps(header).lower()
    length = header.get("bitstream_length") or header.get("config_data_length")
    assert length == 130952


def test_frame_summary_exists():
    summary_path = ROOT / "manifests" / "frame_summary.json"
    assert summary_path.exists(), "Run parse_bitstream.py first"


def test_frame_summary_fields():
    summary = json.loads((ROOT / "manifests" / "frame_summary.json").read_text())
    assert "frame_scan" in summary
    assert summary["frame_scan"]["word_count"] > 0
