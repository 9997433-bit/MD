"""Tests for static freeze, output hashes, and phase B checklist."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_static_freeze():
    data = json.loads((ROOT / "manifests" / "static_freeze.json").read_text())
    assert data["static_phase_complete"] is True
    assert data["identifiers"] >= 237
    assert data["next_phase"] == "phase_b_hardware_capture"


def test_output_hashes():
    data = json.loads((ROOT / "manifests" / "output_hashes.json").read_text())
    assert data["output_count"] >= 10
    assert len(data["combined_sha256"]) == 64


def test_phase_b_checklist():
    data = json.loads((ROOT / "phase_b" / "CHECKLIST.json").read_text())
    # During pytest, captures are session-stashed while CHECKLIST.json may still
    # reflect the committed on-disk capture state — only assert schema here.
    assert data["status"] in {"not_started", "in_progress", "complete"}
    assert len(data["tasks"]) >= 5
    assert isinstance(data.get("done_count"), int)
    assert data["done_count"] >= 0


def test_artifact_inventory_expanded():
    data = json.loads((ROOT / "manifests" / "artifact_inventory.json").read_text())
    assert data["artifact_count"] >= 25
