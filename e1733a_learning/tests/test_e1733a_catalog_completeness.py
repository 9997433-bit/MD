"""Exhaustive catalog completeness tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("identifier", "module", "source_identifier", "status", "boundary")


def _all_entries():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    out = []
    for block in ("acquisition", "analysis", "compensation", "formats"):
        for e in data["catalogs"][block]:
            out.append(e)
    return out, data


def test_no_duplicate_identifiers():
    entries, _ = _all_entries()
    ids = [e["identifier"] for e in entries]
    assert len(ids) == len(set(ids)), f"duplicates: {[i for i in ids if ids.count(i) > 1]}"


def test_minimum_identifier_count():
    entries, data = _all_entries()
    assert len(entries) >= 234
    b = data["catalogs"]
    assert len(b["acquisition"]) >= 82
    assert len(b["analysis"]) >= 80
    assert len(b["compensation"]) >= 53
    assert len(b["formats"]) >= 15


def test_required_fields_present():
    entries, _ = _all_entries()
    for e in entries:
        for f in REQUIRED:
            assert f in e, f"{e.get('identifier')}: missing {f}"
            if f != "source_identifier":
                assert e[f] is not None and e[f] != "", f"{e['identifier']}: empty {f}"


def test_meatype_count_13():
    entries, _ = _all_entries()
    meatypes = [e for e in entries if e["identifier"].startswith("ACQ-E1-MEATYPE-")]
    assert len(meatypes) == 13


def test_cmp_unk_all_unknown():
    entries, _ = _all_entries()
    for e in entries:
        if e["identifier"].startswith("CMP-UNK-"):
            assert e["status"] == "unknown", e["identifier"]


def test_readenvironment_export_unknown():
    entries, _ = _all_entries()
    e = next(
        x for x in entries
        if x.get("source_identifier") == "E1736A_ReadEnvironment" and "ENV" in x["identifier"]
    )
    assert e["status"] == "unknown"


def test_e1736acore_exports_registered():
    entries, _ = _all_entries()
    assert any(e["identifier"].startswith("CMP-E1-CORE-E1736ACore_") for e in entries)
