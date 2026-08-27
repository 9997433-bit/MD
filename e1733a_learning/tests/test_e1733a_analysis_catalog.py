"""Analysis catalog tests: catalog module vs EvidenceLedger.json analysis 段."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "catalogs"))

import catalog_e1733a_ana as ana  # noqa: E402

HEAD_IDS = [
    "ANA-E1-ENTRY-SETUP-ANALYSIS",
    "ANA-E1-ENTRY-OPEN-DATA",
    "ANA-E1-API-READERRORDATA",
]
VIEW_IDS = ["ANA-E1-VIEW-SHOWGRAPH", "ANA-E1-VIEW-RAWDATATABLE"]
GRAPH_IDS = [f"ANA-E1-GRAPH-{n}" for n in (
    "FWD-RUNS", "FWD-MEAN", "FWD-NSIGMA", "REV-RUNS", "REV-MEAN",
    "REV-NSIGMA", "COMB-MEAN", "COMB-NSIGMA", "REMOVE-RAW-OFFSET", "BACKLASH-PT",
)]
NUM_IDS = [f"ANA-E1-NUM-{n}" for n in (
    "ACCURACY", "REPEATABILITY", "MEAN-REV-ERR", "SYS-DEV-POS", "MEAN-BIDIR-POS-DEV",
    "RAW-ACCURACY", "RAW-REPEATABILITY", "MAX-REV-ERR", "SIXSIGMA", "SLOPE",
)]
ISOFIELD_IDS = [
    "ANA-E1-STD-ISOFIELD-MATSEN1", "ANA-E1-STD-ISOFIELD-MATSEN2",
    "ANA-E1-STD-ISOFIELD-MATSEN3", "ANA-E1-STD-ISOFIELD-ATSEN",
    "ANA-E1-STD-ISOFIELD-COMPUSED", "ANA-E1-STD-ISOFIELD-SCALETEMPCOEF",
    "ANA-E1-STD-ISOFIELD-PIECEX", "ANA-E1-STD-ISOFIELD-TOOLZ",
]
DELPHI_SLOTS = [
    "Lin", "Ang", "Str", "Squ", "Par", "Rot", "Way",
    "Fla", "Dia", "LTB", "ATB", "STB", "LDA",
]
UNK_TAIL = ["ANA-UNK-ALG-ISO230-BODY", "ANA-UNK-ALG-VDI-BODY", "ANA-E1-FLA-MOODY"]
CANDIDATE_IDS = [
    "ANA-E1-STD-ISOINFO-ENTRY",
    "ANA-E1-UNC-EXPCOEF", "ANA-E1-UNC-ENVVAR", "ANA-E1-UNC-DIFF20CMAX",
    "ANA-E1-UNC-MATTEMPDEV", "ANA-E1-UNC-ERRORRANGE", "ANA-E1-UNC-ALIGNERR",
    "ANA-E1-UNC-CALMEADEV",
]


def _api_id(ci_constant_name):
    return "ANA-E1-API-ANALYSIS-" + ci_constant_name.replace("E1733A_CI_", "")


ANA_ENTRY_IDS = (
    HEAD_IDS
    + VIEW_IDS
    + [_api_id(ana.ANALYSIS_CI_MAP[ci]) for ci in sorted(ana.ANALYSIS_CI_MAP)]
    + [f"ANA-E1-STD-{i}" for i in sorted(ana.STANDARDS_MAP)]
    + GRAPH_IDS
    + NUM_IDS
    + ISOFIELD_IDS
    + [f"ANA-UNK-DELPHI-{s.upper()}DOC" for s in DELPHI_SLOTS]
    + UNK_TAIL
    + CANDIDATE_IDS
)


def test_ana_entry_ids_match_ledger_order_exactly():
    ledger_ids = ana.analysis_entry_ids()
    assert len(ANA_ENTRY_IDS) == len(set(ANA_ENTRY_IDS))
    assert len(ledger_ids) == len(set(ledger_ids))
    assert ANA_ENTRY_IDS == ledger_ids


def test_standards_map_matches_std_entries():
    assert len(ana.STANDARDS_MAP) == 13
    assert set(ana.STANDARDS_MAP) == set(range(13))
    by_id = {e["identifier"]: e for e in ana.standard_entries()}
    assert len(by_id) == 13
    for idx, name in ana.STANDARDS_MAP.items():
        entry = by_id[f"ANA-E1-STD-{idx}"]
        assert entry["source_identifier"] == f"ANASETUP_STANDARD_CHOOSING={idx}"
        assert entry["status"] == "E1"


def test_analysis_ci_map_matches_api_entries():
    assert len(ana.ANALYSIS_CI_MAP) == 46
    by_id = {e["identifier"]: e for e in ana.analysis_entries()}
    api_ids_in_ledger = {i for i in by_id if i.startswith("ANA-E1-API-ANALYSIS-")}
    expected_api_ids = {_api_id(n) for n in ana.ANALYSIS_CI_MAP.values()}
    assert api_ids_in_ledger == expected_api_ids
    assert ana.verify_analysis_ci_map() == []


def test_unknown_entries_status_still_unknown():
    unknown = [e for e in ana.analysis_entries() if e["identifier"].startswith("ANA-UNK-")]
    assert len(unknown) == 15  # 13 Delphi + ISO230 + VDI bodies
    for entry in unknown:
        assert entry["status"] == "unknown"
        assert entry["window_hash"] is None
    assert len(ana.unknown_delphi_slots()) == 13
