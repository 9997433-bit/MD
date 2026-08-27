"""Unified static catalog API for E1733A learning package."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
Block = Literal["acquisition", "analysis", "compensation", "formats"]


def load_ledger() -> dict[str, Any]:
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def load_coverage() -> dict[str, Any]:
    return json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))


def load_bridge_matrix() -> dict[str, Any]:
    return json.loads((ROOT / "bridge_matrix.json").read_text(encoding="utf-8"))


def entries_by_block(block: Block) -> list[dict[str, Any]]:
    return load_ledger()["catalogs"][block]


def all_entries() -> list[dict[str, Any]]:
    ledger = load_ledger()
    out: list[dict[str, Any]] = []
    for block in ("acquisition", "analysis", "compensation", "formats"):
        for e in ledger["catalogs"][block]:
            out.append({**e, "block": block})
    return out


def get_entry(identifier: str) -> dict[str, Any] | None:
    for e in all_entries():
        if e["identifier"] == identifier:
            return e
    return None


def identifiers() -> list[str]:
    return [e["identifier"] for e in all_entries()]


def unknown_entries() -> list[dict[str, Any]]:
    return [e for e in all_entries() if e["status"] == "unknown"]


def forced_null_bridges() -> list[str]:
    return load_bridge_matrix()["forced_null_bridges"]
