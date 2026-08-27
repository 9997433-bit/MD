"""Compensation catalog entries for E1733A static analysis."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_ledger() -> dict[str, Any]:
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def compensation_entries() -> list[dict[str, Any]]:
    return load_ledger()["catalogs"]["compensation"]


# 顺序与 EvidenceLedger.json 中 compensation 段一致
CMP_ENTRY_IDS = [e["identifier"] for e in compensation_entries()]


def get_entry(identifier: str) -> dict[str, Any] | None:
    for e in compensation_entries():
        if e["identifier"] == identifier:
            return e
    return None


def cmp_setup_fields() -> list[dict[str, Any]]:
    """Ledger rows anchored on CMPSETUP / ENVSETUP Remote.h constants."""
    return [
        e
        for e in compensation_entries()
        if e["identifier"].startswith("CMP-E1-CFG-")
        or e["identifier"].startswith("CMP-E1-UI-")
        or "ENVSETUP" in (e.get("source_identifier") or "")
    ]


def verify_no_unk_upgrades() -> list[str]:
    """Ensure CMP-UNK-* rows were not mislabeled as E1."""
    violations = []
    for e in compensation_entries():
        if e["identifier"].startswith("CMP-UNK-") and e["status"] == "E1":
            violations.append(e["identifier"])
    return violations


def window_audit() -> dict[str, dict[str, Any]]:
    """Status/source/missing snapshot for CMP-UNK-* and CMP-E1-* rows."""
    return {
        e["identifier"]: {
            "status": e["status"],
            "source": e.get("source_identifier"),
            "missing": e.get("missing"),
        }
        for e in compensation_entries()
        if e["identifier"].startswith("CMP-UNK") or e["identifier"].startswith("CMP-E1")
    }
