"""Analysis catalog completeness tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "catalogs"))

import catalog_e1733a_ana as ana  # noqa: E402


def test_ana_entry_ids_match_ledger():
    ledger_ids = ana.analysis_entry_ids()
    assert set(ana.ANA_ENTRY_IDS) == set(ledger_ids)
    assert ana.ANA_ENTRY_IDS == ledger_ids


def test_all_analysis_ci_present():
    for i in range(28):
        assert any(
            f"CI={i}" in (e.get("source_identifier") or "")
            for e in ana.analysis_entries()
        ), f"missing CC_ANALYSIS CI={i}"


def test_standards_map_matches_ledger():
    assert ana.verify_standards_map() == []
    assert ana.verify_analysis_ci_map() == []


def test_standards_0_to_12():
    ids = {e["identifier"] for e in ana.analysis_entries()}
    for i in range(13):
        assert f"ANA-E1-STD-{i}" in ids


def test_delphi_slots_registered():
    ids = {e["identifier"] for e in ana.analysis_entries()}
    for slot in ["LINDOC", "ANGDOC", "STRDOC", "SQU", "FLA", "DIA", "LTB", "LDA"]:
        assert any(slot in i for i in ids)


def test_unk_entries_remain_unknown():
    for ident in ["ANA-UNK-ALG-ISO230-BODY"]:
        row = ana.get_entry(ident)
        assert row is not None
        assert row["status"] == "unknown"
