"""Tests for checklist report and phase transition detection."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_checklist_report():
    text = (ROOT / "CHECKLIST_REPORT.md").read_text()
    assert "B1" in text
    assert "C1" in text


def test_phase_transition_static():
    data = json.loads((ROOT / "manifests" / "phase_transition.json").read_text())
    assert data["current_phase"] == "static_complete_pending_hardware"
    assert data["recommended_phase"] == "static_complete_pending_hardware"
    assert data["transition_ready"] is False
