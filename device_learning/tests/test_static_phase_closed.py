"""Assert static phase is closed and frozen."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_static_phase_closed_marker():
    data = json.loads((ROOT / "manifests" / "static_phase_closed.json").read_text())
    assert data["static_phase_closed"] is True


def test_frozen_matches_closed():
    freeze = json.loads((ROOT / "manifests" / "static_freeze.json").read_text())
    assert freeze["static_phase_complete"] is True
    pkg = json.loads((ROOT / "manifests" / "package_manifest.json").read_text())
    assert pkg["version"] == "static-1.0"
