"""Catalog completeness for Firebolt learning skeleton."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("identifier", "module", "source_identifier", "status", "boundary")
BLOCKS = ("spec", "hardware", "fx3", "bitstream", "learn")


def _ledger():
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def _all_entries():
    data = _ledger()
    out = []
    for block in BLOCKS:
        for e in data["catalogs"][block]:
            out.append({**e, "block": block})
    return out, data


def test_ledger_exists():
    assert (ROOT / "EvidenceLedger.json").is_file()
    assert (ROOT / "coverage.json").is_file()


def test_no_duplicate_identifiers():
    entries, _ = _all_entries()
    ids = [e["identifier"] for e in entries]
    assert len(ids) == len(set(ids))


def test_required_fields():
    entries, _ = _all_entries()
    for e in entries:
        for f in REQUIRED:
            assert f in e and e[f] not in (None, ""), f"{e.get('identifier')}: {f}"


def test_block_minimums():
    _, data = _all_entries()
    assert len(data["catalogs"]["spec"]) >= 12
    assert len(data["catalogs"]["hardware"]) >= 8
    assert len(data["catalogs"]["fx3"]) >= 10
    assert len(data["catalogs"]["bitstream"]) >= 5
    assert len(data["catalogs"]["learn"]) >= 6
    assert data["stats"]["identifier_count"] >= 40


def test_spec_sync_core_confirmed():
    entries, _ = _all_entries()
    need = {
        "SPEC-ADC-16",
        "SPEC-SIM-MAX-16CH",
        "SPEC-SE-PAIR",
        "SPEC-BANK",
        "SPEC-AICONV-RATE",
        "SPEC-SYNC-LAYER",
    }
    got = {e["identifier"]: e for e in entries if e["identifier"] in need}
    assert set(got) == need
    for e in got.values():
        assert e["status"] == "confirmed"


def test_unknowns_include_deferred():
    entries, _ = _all_entries()
    unk = {e["identifier"] for e in entries if e["status"] == "unknown"}
    for i in (
        "FX3-REGMAP",
        "FX3-FUSION-REQ",
        "BIT-SYNC-CLOCK-TREE",
        "BIT-BANK-AICONV",
        "HW-ADC-MPN",
    ):
        assert i in unk


def test_bridge_forced_null_min():
    bridge = json.loads((ROOT / "bridge_matrix.json").read_text(encoding="utf-8"))
    assert len(bridge["forced_null_bridges"]) >= 8
    for cell in bridge["cells"].values():
        assert cell["proven_bridge"] is None
