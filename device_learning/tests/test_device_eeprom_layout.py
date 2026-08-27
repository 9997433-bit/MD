"""Tests for FX2LP EEPROM layout parsing."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_parse import parse_eeprom  # noqa: E402


def test_synthetic_eeprom_c2_layout():
    fixture = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
    data = fixture.read_bytes()
    hdr = parse_eeprom(data)
    assert hdr.boot_format == "C2"
    assert hdr.vid == 0x0000
    assert hdr.pid == 0x0000
    assert hdr.firmware_offset == 12
    assert hdr.firmware_size_bytes == 16


def test_eeprom_meta_uses_public_offsets():
    meta = json.loads((ROOT / "manifests" / "eeprom_meta.json").read_text())
    assert meta.get("boot_format") == "C2"
    assert meta.get("firmware_offset") == 12


def test_bom_crosswalk_exists():
    path = ROOT / "manifests" / "bom_crosswalk.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["linked_count"] >= 10


def test_config_entropy_manifest():
    path = ROOT / "manifests" / "config_entropy.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["byte_entropy_bits"] > 0


def test_identifier_index_md():
    path = ROOT / "IDENTIFIER_INDEX.md"
    assert path.exists()
    assert "HW-001-FPGA-DEVICE" in path.read_text()
