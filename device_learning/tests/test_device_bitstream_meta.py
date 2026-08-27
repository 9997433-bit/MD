"""Test bitstream metadata fields."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_bit import ENTRIES as BIT_ENTRIES

CONFIRMED_FROM_FRAME_SUMMARY = [
    "BIT-SYNC-WORD",
    "BIT-IDCODE",
    "BIT-FLR",
    "BIT-COR",
    "BIT-CRC",
    "BIT-CMD-SEQUENCE",
    "BIT-FDRI-WORD-COUNT",
    "BIT-FRAME-COUNT-EST",
]


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


def test_frame_summary_confirmed_entries_present():
    by_id = {e["identifier"]: e for e in BIT_ENTRIES}
    missing = [i for i in CONFIRMED_FROM_FRAME_SUMMARY if i not in by_id]
    assert not missing, f"Missing bit catalog entries: {missing}"


def test_frame_summary_confirmed_entries_status():
    by_id = {e["identifier"]: e for e in BIT_ENTRIES}
    not_confirmed = [
        i for i in CONFIRMED_FROM_FRAME_SUMMARY
        if by_id[i]["status"] != "confirmed"
    ]
    assert not not_confirmed, f"Expected confirmed status: {not_confirmed}"


def test_frame_summary_confirmed_entries_cite_frame_summary():
    by_id = {e["identifier"]: e for e in BIT_ENTRIES}
    bad_evidence = [
        i for i in CONFIRMED_FROM_FRAME_SUMMARY
        if "frame_summary" not in (by_id[i].get("evidence") or "")
    ]
    assert not bad_evidence, f"Evidence must cite frame_summary: {bad_evidence}"


def test_iob_candidate_config_words_reference():
    by_id = {e["identifier"]: e for e in BIT_ENTRIES}
    iob = by_id["IOB-001-ACTIVE-COUNT"]
    assert iob["status"] == "candidate"
    blob = f"{iob.get('description', '')} {iob.get('evidence', '')}"
    assert "223" in blob or "candidate_iob_config_words" in blob
