"""Analysis catalog entries for E1733A static analysis.

Evidence boundary: every constant below is transcribed from Remote.h
(E1733A_Remote.h, frozen in manifests/setup_constants.json). No value here
comes from binary reverse engineering; formula bodies remain unknown (E1).
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

# ANASETUP_STANDARD_CHOOSING (Remote.h index 81) enumerates the analysis
# standard selectable in [Data Analysis] -> Standard. Index -> standard name.
STANDARDS_MAP = {
    0: "NMTBA w/o Offset",
    1: "NMTBA",
    2: "ANSI B5.54/B5.57",
    3: "VDI 3441/2617",
    4: "BSI 3800",
    5: "JIS B6330",
    6: "ISO 230-2 1988",
    7: "ISO 230-2 1997",
    8: "GB10931-89",
    9: "GB/T 17421.2-2000",
    10: "User",
    11: "ISO 230-2 2006",
    12: "ISO 230-2 2014",
}

# E1733A_CC_ANALYSIS (=66) result selectors: CI index -> Remote.h constant
# name (E1733A_CI_xxxx). The message returns the metric as a 4-byte float.
#
# ISO uncertainty note (E1 boundary only). Remote.h labels CI 0-11 with the
# symbol set B, ~B, M, E-, E+, E, R-, R+, R, A-, A+, A. These symbols match
# the metric names used by the ISO 230-2 positioning standards that appear in
# STANDARDS_MAP (indexes 6/7/11/12), where R and A are uncertainty-style
# quantities built from an estimator times a coverage factor. Remote.h also
# exposes a [Data Analysis] -> "Coverage Factor (Sigma)" setting
# (E1733A_CI_ANASETUP_ANASIGMA_ITEMTEXT = 74). What is proven here stops at
# these header labels: the actual estimator, coverage-factor application, and
# per-standard formula bodies are NOT transcribed anywhere and remain unknown
# (see ledger entry ANA-UNK-ALG-ISO230-BODY, boundary no_instruction_window).
# Do not infer formulas from the symbol names.
ANALYSIS_CI_MAP = {
    0: "E1733A_CI_BIMAXREV",       # Remote.h: "B, max reversl error" (sic)
    1: "E1733A_CI_BIMEANREV",      # Remote.h: "~B, mean reversal error"
    2: "E1733A_CI_BIMEANDEV",      # Remote.h: "M, mean bi-directional positin deviation" (sic)
    3: "E1733A_CI_REVSYSPOSDEV",   # Remote.h: "E-, Mean positional deviation, backward"
    4: "E1733A_CI_FWDSYSPOSDEV",   # Remote.h: "E+, Mean positional deviation, forward"
    5: "E1733A_CI_BISYSPOSDEV",    # Remote.h: "E, Mean positional deviation, bi-directional"
    6: "E1733A_CI_REVREPEATPOS",   # Remote.h: "R-, Repeatabolity, backward" (sic)
    7: "E1733A_CI_FWDREPEATPOS",   # Remote.h: "R+, Repeatabolity, forward" (sic)
    8: "E1733A_CI_BIREPEATPOS",    # Remote.h: "R, Repeatabolity, bi-directional" (sic)
    9: "E1733A_CI_REVACCURACY",    # Remote.h: "A-, Accuracy, backward"
    10: "E1733A_CI_FWDACCURACY",   # Remote.h: "A+, Accuracy, forward"
    11: "E1733A_CI_BIACCURACY",    # Remote.h: "A, Accuracy, bi-directional"
    12: "E1733A_CI_REVRAWREP",
    13: "E1733A_CI_FWDRAWREP",
    14: "E1733A_CI_BIRAWREP",
    15: "E1733A_CI_REVRAWACC",
    16: "E1733A_CI_FWDRAWACC",
    17: "E1733A_CI_BIRAWACC",
    18: "E1733A_CI_SIXSIGMA",
    19: "E1733A_CI_SLOPELS",
    20: "E1733A_CI_SLOPEEP",
    21: "E1733A_CI_VDI_P",
    22: "E1733A_CI_VDI_PSMAX",
    23: "E1733A_CI_VDI_PSMEAN",
    24: "E1733A_CI_VDI_PSU",
    25: "E1733A_CI_VDI_PA",
    26: "E1733A_CI_VDI_UMAX",
    27: "E1733A_CI_VDI_UMEAN",
    30: "E1733A_CI_MAX_ELEVATION",
    31: "E1733A_CI_CLOSURE_DH",
    32: "E1733A_CI_CLOSURE_BF",
    33: "E1733A_CI_PAR_RESULT",
    34: "E1733A_CI_SQU_RESULT",
    35: "E1733A_CI_PLUSMINUS",
    40: "E1733A_CI_POS_MAX",
    41: "E1733A_CI_POS_MIN",
    42: "E1733A_CI_POS_MEAN",
    43: "E1733A_CI_POS_NSIGMA",
    44: "E1733A_CI_VEL_MAX",
    45: "E1733A_CI_VEL_MIN",
    46: "E1733A_CI_VEL_MEAN",
    47: "E1733A_CI_VEL_NSIGMA",
    48: "E1733A_CI_ACC_MAX",
    49: "E1733A_CI_ACC_MIN",
    50: "E1733A_CI_ACC_MEAN",
    51: "E1733A_CI_ACC_NSIGMA",
}


def load_ledger():
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def analysis_entries():
    return load_ledger()["catalogs"]["analysis"]


def analysis_entry_ids():
    """Return every analysis catalog identifier, in ledger order."""
    return [e["identifier"] for e in analysis_entries()]


# 顺序与 EvidenceLedger.json 中 analysis 段一致
ANA_ENTRY_IDS = analysis_entry_ids()


def get_entry(identifier: str):
    for e in analysis_entries():
        if e["identifier"] == identifier:
            return e
    return None


def verify_standards_map():
    """Cross-check STANDARDS_MAP indexes against ANA-E1-STD-* ledger rows."""
    mismatches = []
    for idx, name in STANDARDS_MAP.items():
        ident = f"ANA-E1-STD-{idx}"
        row = get_entry(ident)
        if row is None:
            mismatches.append(f"{ident}: missing from ledger")
        elif f"ANASETUP_STANDARD_CHOOSING={idx}" not in (row.get("source_identifier") or ""):
            mismatches.append(f"{ident}: source {row.get('source_identifier')!r}")
    return mismatches


def standard_entries():
    """Return the ANA-E1-STD-* ledger entries (analysis standard slots)."""
    return [
        e for e in analysis_entries() if e["identifier"].startswith("ANA-E1-STD-")
    ]


def unknown_delphi_slots():
    """Return unresolved Delphi document slots (status=unknown, no RTTI).

    Each item maps the ledger identifier to its logical slot name, e.g.
    ANA-UNK-DELPHI-LINDOC -> "Lin". These are the analysis document classes
    whose RVAs are still unproven in E1733A.exe.
    """
    slots = []
    for e in analysis_entries():
        if e["status"] != "unknown" or e["boundary"] != "no_rtti":
            continue
        source = e.get("source_identifier") or ""
        slot = source.split("=", 1)[1] if "=" in source else None
        slots.append({"identifier": e["identifier"], "logical_slot": slot})
    return slots


def load_setup_constants():
    """Load the frozen Remote.h constant manifest (name/value/comment)."""
    return json.loads(
        (ROOT / "manifests" / "setup_constants.json").read_text(encoding="utf-8")
    )


def setup_constant_value(name):
    """Return the raw string value of one Remote.h constant, or None."""
    for c in load_setup_constants()["constants"]:
        if c["name"] == name:
            return c["value"]
    return None


def analysis_ci_constants():
    """Return manifest rows for the CC_ANALYSIS CI selectors (index order)."""
    by_name = {c["name"]: c for c in load_setup_constants()["constants"]}
    return {ci: by_name[name] for ci, name in ANALYSIS_CI_MAP.items() if name in by_name}


def verify_analysis_ci_map():
    """Cross-check ANALYSIS_CI_MAP indexes against the frozen manifest.

    Returns a list of mismatch strings; empty list means the map agrees
    with manifests/setup_constants.json.
    """
    mismatches = []
    by_name = {c["name"]: c["value"] for c in load_setup_constants()["constants"]}
    for ci, name in ANALYSIS_CI_MAP.items():
        value = by_name.get(name)
        if value is None:
            mismatches.append(f"{name}: missing from setup_constants.json")
        elif value.strip() != str(ci):
            mismatches.append(f"{name}: manifest value {value!r} != CI {ci}")
    return mismatches
