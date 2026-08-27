"""Compensation catalog entries for E1733A static analysis."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load_ledger():
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def compensation_entries():
    return load_ledger()["catalogs"]["compensation"]


def window_audit():
  entries = compensation_entries()
  return {
      e["identifier"]: {
          "status": e["status"],
          "source": e.get("source_identifier"),
          "missing": e.get("missing"),
      }
      for e in entries
      if e["identifier"].startswith("CMP-UNK")
  }
