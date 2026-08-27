"""Analysis catalog completeness tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_all_analysis_ci_present():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    for i in range(28):
        assert any(
            f"CI={i}" in (e.get("source_identifier") or "")
            for e in data["catalogs"]["analysis"]
        ), f"missing CC_ANALYSIS CI={i}"


def test_standards_0_to_12():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    ids = {e["identifier"] for e in data["catalogs"]["analysis"]}
    for i in range(13):
        assert f"ANA-E1-STD-{i}" in ids


def test_delphi_slots_registered():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    ids = {e["identifier"] for e in data["catalogs"]["analysis"]}
    for slot in ["LINDOC", "ANGDOC", "STRDOC", "SQU", "FLA", "DIA", "LTB", "LDA"]:
        assert any(slot in i for i in ids)
