"""Static catalog API smoke tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs import static_catalog  # noqa: E402
from catalogs.catalog_spec_sync import entry_ids as spec_ids  # noqa: E402


def test_static_catalog_api():
    assert len(static_catalog.identifiers()) >= 40
    assert static_catalog.get_entry("SPEC-ADC-16")["status"] == "confirmed"
    assert len(static_catalog.forced_null_bridges()) >= 8
    unk = static_catalog.unknown_entries()
    assert any(e["identifier"] == "FX3-FUSION-REQ" for e in unk)


def test_spec_ids_match_ledger():
    ids = set(spec_ids())
    ledger_ids = {
        e["identifier"] for e in static_catalog.entries_by_block("spec")
    }
    assert ids == ledger_ids
