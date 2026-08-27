"""Format disposition catalog for E1733A Option Description Files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

EXT_TO_SLOT = {
    ".lin": "Lin", ".ang": "Ang", ".str": "Str", ".squ": "Squ", ".par": "Par",
    ".rot": "Rot", ".way": "Way", ".fla": "Fla", ".dia": "Dia", ".ltb": "LTB",
    ".atb": "ATB", ".stb": "STB", ".lda": "LDA",
}


def load_ledger() -> dict[str, Any]:
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def format_entries() -> list[dict[str, Any]]:
    return load_ledger()["catalogs"]["formats"]


def format_disposition() -> dict[str, str]:
    return {e["identifier"]: e.get("disposition", e.get("status", "")) for e in format_entries()}


def format_by_extension(ext: str) -> dict[str, Any] | None:
    ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
    slot = EXT_TO_SLOT.get(ext)
    if not slot:
        return None
    ident = f"FMT-{ext[1:].upper()}"
    for e in format_entries():
        if e["identifier"] == ident:
            return e
    return None
