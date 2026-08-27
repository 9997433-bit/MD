"""Tests for firmware extract, protocol log, and capture manifest."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"
FW_OUT = ROOT / "phase_b" / "analysis" / "firmware.bin"


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_extract_firmware_slice_synthetic(synthetic_eeprom_capture):
    result = _run("extract_firmware_slice.py", "--allow-synthetic")
    assert result.returncode == 0, result.stderr
    meta = json.loads((ROOT / "manifests" / "firmware_extract.json").read_text())
    assert meta["status"] == "extracted"
    assert FW_OUT.exists()
    assert FW_OUT.stat().st_size == meta["firmware_size_bytes"]


def test_extract_firmware_slice_rejects_capture_without_flag(synthetic_eeprom_capture):
    result = _run("extract_firmware_slice.py")
    assert result.returncode == 2
    meta = json.loads((ROOT / "manifests" / "firmware_extract.json").read_text())
    assert meta["status"] == "rejected"


def test_analyze_protocol_log_missing():
    proto = ROOT / "phase_b" / "captures" / "protocol_log.json"
    if proto.exists():
        proto.unlink()
    result = _run("analyze_protocol_log.py")
    assert result.returncode == 0
    meta = json.loads((ROOT / "manifests" / "protocol_log_meta.json").read_text())
    assert meta["status"] == "missing"


def test_build_capture_manifest():
    _run("build_capture_manifest.py")
    data = json.loads((ROOT / "manifests" / "capture_manifest.json").read_text())
    assert "artifacts" in data
    assert data["expected_count"] >= 6
