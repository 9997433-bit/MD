"""Unknown export window audit tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _entries():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    return data["catalogs"]["compensation"] + data["catalogs"]["acquisition"]


def test_process_raw_data_stays_unknown():
    hits = [e for e in _entries() if "ProcessRawData" in (e.get("source_identifier") or "")]
    assert hits
    assert all(e["status"] == "unknown" for e in hits if e["identifier"].startswith("ACQ-E1-CORE"))


def test_ambient_body_stays_unknown():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    e = next(x for x in data["catalogs"]["compensation"] if x["identifier"] == "CMP-UNK-AMBIENT-BODY")
    assert e["status"] == "unknown"


def test_interpolate_stays_unknown():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    e = next(x for x in data["catalogs"]["compensation"] if x["identifier"] == "CMP-UNK-INTERPOLATE-ALG")
    assert e["status"] == "unknown"


def test_delphi_runtime_exports_registered_across_dlls():
    """Four vendor DLLs each export the same Delphi runtime trio; all should be in ledger."""
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    entries = data["catalogs"]["acquisition"] + data["catalogs"]["compensation"]
    sym = "TMethodImplementationIntercept"
    hits = [e for e in entries if e.get("source_identifier") == sym]
    assert len(hits) == 4
    modules = {e["module"] for e in hits}
    assert modules == {"E1735A.dll", "E1735ACore.dll", "E1736A.dll", "E1736ACore.dll"}
