"""Test learning layer and indexes."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_photo_index():
    data = json.loads((ROOT / "manifests" / "photo_index.json").read_text())
    assert data["photo_count"] == 10
    assert sum(p["component_count"] for p in data["photos"]) > 20


def test_crossref_index():
    data = json.loads((ROOT / "manifests" / "crossref_index.json").read_text())
    assert data["total_identifiers"] >= 200
    assert "usb_path" in data["themes"]


def test_learn_catalog_in_ledger():
    ledger = json.loads((ROOT / "EvidenceLedger.json").read_text())
    assert len(ledger["catalogs"]["learn"]) >= 20


def test_no_sensitive_design_name_in_manifests():
    text = (ROOT / "manifests" / "bitstream_meta.json").read_text().lower()
    assert "topusb" not in text
    assert "4431" not in text


def test_learning_guide_exists():
    assert (ROOT / "LEARNING_GUIDE.md").exists()
