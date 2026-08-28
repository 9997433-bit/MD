"""Validate all manifest JSON files and phase checklists."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_all_manifests_parse():
    bad = []
    for p in (ROOT / "manifests").glob("*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append(p.name)
    assert not bad, f"Invalid JSON: {bad}"


def test_phase_c_checklist():
    data = json.loads((ROOT / "phase_c" / "CHECKLIST.json").read_text())
    assert data["status"] == "not_started"
    assert data["done_count"] == 0
    assert len(data["tasks"]) >= 5


def test_health_check_script_exists():
    assert (ROOT / "scripts" / "health_check.py").exists()


def test_health_allows_phase_b_captures():
    """Real USB/protocol captures are expected once Phase B starts."""
    from scripts import health_check as hc

    ok, detail = hc.captures_clean()
    assert ok, detail
    names = {p.name for p in hc.CAPTURES.iterdir() if p.is_file()}
    assert names <= hc.ALLOWED_CAPTURE_NAMES
