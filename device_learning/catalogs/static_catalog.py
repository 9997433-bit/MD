"""Unified static catalog API."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def make_entry(identifier, layer, module, description, status, boundary, evidence):
    return {
        "identifier": identifier,
        "layer": layer,
        "module": module,
        "description": description,
        "status": status,
        "boundary": boundary,
        "evidence": evidence,
    }


def load_ledger() -> dict[str, Any]:
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def load_coverage() -> dict[str, Any]:
    return json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
