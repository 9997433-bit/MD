"""Acquisition catalog tests: catalog module vs EvidenceLedger.json.

只读校验 catalogs/catalog_e1733a_acq.py 与 ledger acquisition 段的一致性,
不修改 generate_ledger,也不推断任何未证实的行为。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "catalogs"))

import catalog_e1733a_acq as acq  # noqa: E402


def test_acq_entry_ids_match_ledger_exactly():
    ledger_ids = [e["identifier"] for e in acq.acquisition_entries()]
    # 两侧均不允许重复
    assert len(acq.ACQ_ENTRY_IDS) == len(set(acq.ACQ_ENTRY_IDS))
    assert len(ledger_ids) == len(set(ledger_ids))
    # 条目集合完全一致（并行生成的 ledger 采用追加顺序，故不比较排序）
    assert set(acq.ACQ_ENTRY_IDS) == set(ledger_ids)
    assert len(acq.ACQ_ENTRY_IDS) == len(ledger_ids)


def test_meatype_ids_length_13():
    assert len(acq.meatype_ids()) == 13


def test_process_raw_data_status_unknown():
    entry = acq.get_entry("ACQ-E1-CORE-E1735ACore_ProcessRawData")
    assert entry is not None
    assert entry["status"] == "unknown"
