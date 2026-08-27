"""Test synthetic EEPROM pipeline."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_eeprom_fixture():
    fixture = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
    assert fixture.exists(), "Run build_eeprom_synthetic.py first (via generate_ledger.py)"


def test_eeprom_meta_not_missing_after_synthetic():
    meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
    assert meta["status"] in ("synthetic_pipeline_test", "observed")
    assert "sha256" in meta


def test_eeprom_synthetic_meta():
    p = ROOT / "manifests" / "eeprom_synthetic_meta.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["type"] == "synthetic_reference"
