"""Test all catalog entries have non-empty status."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_arch import ENTRIES as ARCH_ENTRIES
from catalogs.catalog_bit import ENTRIES as BIT_ENTRIES
from catalogs.catalog_hw import ENTRIES as HW_ENTRIES
from catalogs.catalog_exp import ENTRIES as EXP_ENTRIES
from catalogs.catalog_learn import ENTRIES as LEARN_ENTRIES
from catalogs.catalog_ref import ENTRIES as REF_ENTRIES
from catalogs.catalog_signal import ENTRIES as SIG_ENTRIES
from catalogs.catalog_usb import ENTRIES as USB_ENTRIES


def test_no_empty_status():
    all_entries = HW_ENTRIES + BIT_ENTRIES + SIG_ENTRIES + USB_ENTRIES + REF_ENTRIES + ARCH_ENTRIES + LEARN_ENTRIES + EXP_ENTRIES
    empty = [e["identifier"] for e in all_entries if not e.get("status")]
    assert not empty, f"Empty status: {empty}"


def test_minimum_entry_count():
    total = len(HW_ENTRIES) + len(BIT_ENTRIES) + len(SIG_ENTRIES) + len(USB_ENTRIES) + len(REF_ENTRIES) + len(ARCH_ENTRIES) + len(LEARN_ENTRIES) + len(EXP_ENTRIES)
    assert total >= 230, f"Only {total} entries, need >= 230"
