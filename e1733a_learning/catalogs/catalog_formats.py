"""Format disposition catalog for E1733A Option Description Files."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load_ledger():
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def format_entries():
    return load_ledger()["catalogs"]["formats"]


def format_disposition():
    return {e["identifier"]: e.get("disposition", e.get("status")) for e in format_entries()}
