"""English.csv gap manifest tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_english_gaps_file_exists():
    p = ROOT / "manifests" / "english_string_gaps.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["ledger_has_string_id_anchors"] is True
    assert len(data["gap_blocks"]) >= 5


def test_forced_null_reminders_present():
    data = json.loads((ROOT / "manifests" / "english_string_gaps.json").read_text(encoding="utf-8"))
    assert any("Edlen" in r or "Wavelength" in r for r in data["forced_null_reminders"])


def test_top_priority_candidates_in_ledger():
    gaps = json.loads((ROOT / "manifests" / "english_string_gaps.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    ids = {e["identifier"] for cat in ledger["catalogs"].values() for e in cat}
    expected = [
        "CMP-E1-ENV-UI-SHOWENV",
        "CMP-E1-ENV-CFG-AIRPRES",
        "CMP-E1-ENV-CFG-AIRTEMP",
        "CMP-E1-ENV-CFG-RELHUMI",
        "CMP-E1-ENV-CFG-MATTEMP1",
        "CMP-E1-ENV-CFG-MATTEMP2",
        "CMP-E1-ENV-CFG-MATTEMP3",
        "CMP-E1-ENV-CFG-UNITSEL",
        "CMP-E1-CFG-TABLE-START",
        "CMP-E1-CFG-TABLE-END",
        "CMP-E1-CFG-TABLE-INTERVAL",
        "ANA-E1-STD-ISOINFO-ENTRY",
        "ANA-E1-UNC-EXPCOEF",
        "ANA-E1-UNC-ENVVAR",
    ]
    for ident in expected:
        assert ident in ids, f"missing Top-10 candidate: {ident}"
        row = next(e for cat in ledger["catalogs"].values() for e in cat if e["identifier"] == ident)
        assert row["status"] == "candidate"
    assert len(gaps["top_priority_candidates"]) == 10
