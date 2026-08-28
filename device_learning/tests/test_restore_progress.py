"""Tests for EP84 unpack preview and restore crosscheck."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"


@pytest.mark.skipif(not SESSION.exists(), reason="usb_session.pcapng missing")
def test_ep84_unpack_preview_candidate_only():
    path = ROOT / "manifests" / "ep84_unpack_preview.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "preview":
        return
    assert data.get("confidence") == "candidate"
    assert data.get("payloads_decoded", 0) >= 1
    assert "4431" not in path.read_text()


def test_restore_crosscheck_partial():
    path = ROOT / "manifests" / "restore_crosscheck.json"
    progress = ROOT / "RESTORE_PROGRESS.md"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("status") == "partial_restore"
    assert data.get("confidence_ceiling") == "candidate"
    assert data.get("overall_restore_fraction_estimate", 1) < 1.0
    assert progress.exists()
    assert "4431" not in progress.read_text()
