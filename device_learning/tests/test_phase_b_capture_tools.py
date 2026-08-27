"""Tests for firmware extract, protocol log, and capture manifest."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"
FW_OUT = ROOT / "phase_b" / "analysis" / "firmware.bin"
PROTO = ROOT / "phase_b" / "captures" / "protocol_log.json"
TEMPLATE = ROOT / "phase_b" / "templates" / "protocol_log_template.json"


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def synthetic_eeprom_capture():
    CAPTURE.parent.mkdir(parents=True, exist_ok=True)
    backup = CAPTURE.read_bytes() if CAPTURE.exists() else None
    shutil.copy(SYNTH, CAPTURE)
    yield
    if backup is not None:
        CAPTURE.write_bytes(backup)
    elif CAPTURE.exists():
        CAPTURE.unlink()
    if FW_OUT.exists():
        FW_OUT.unlink()


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
    backup = PROTO.read_bytes() if PROTO.exists() else None
    if PROTO.exists():
        PROTO.unlink()
    try:
        result = _run("analyze_protocol_log.py")
        assert result.returncode == 0
        meta = json.loads((ROOT / "manifests" / "protocol_log_meta.json").read_text())
        assert meta["status"] == "missing"
    finally:
        if backup is not None:
            PROTO.write_bytes(backup)
        elif PROTO.exists():
            PROTO.unlink()


def test_analyze_protocol_log_template_invalid():
    backup = PROTO.read_bytes() if PROTO.exists() else None
    shutil.copy(TEMPLATE, PROTO)
    try:
        _run("analyze_protocol_log.py")
        meta = json.loads((ROOT / "manifests" / "protocol_log_meta.json").read_text())
        assert meta["status"] == "invalid"
        assert meta["command_count"] >= 1
    finally:
        if backup is not None:
            PROTO.write_bytes(backup)
        elif PROTO.exists():
            PROTO.unlink()


def test_build_capture_manifest():
    _run("build_capture_manifest.py")
    data = json.loads((ROOT / "manifests" / "capture_manifest.json").read_text())
    assert "artifacts" in data
    assert data["expected_count"] >= 6
