"""Analysis catalog entries for E1733A static analysis."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load_ledger():
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def analysis_entries():
    return load_ledger()["catalogs"]["analysis"]
