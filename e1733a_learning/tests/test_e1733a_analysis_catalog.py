"""Analysis catalog tests: catalog module vs EvidenceLedger.json analysis 段.

只读校验 catalogs/catalog_e1733a_ana.py 与 ledger analysis 段的一致性,
不修改 static_catalog/generate_ledger,也不推断任何未证实的行为。
catalog 模块本身不导出 ANA_ENTRY_IDS,故在测试内按 generate_ledger
build_ana_catalog 的追加顺序由 STANDARDS_MAP / ANALYSIS_CI_MAP 推导。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "catalogs"))

import catalog_e1733a_ana as ana  # noqa: E402

# generate_ledger.build_ana_catalog 的固定头部条目(顺序即追加顺序)
HEAD_IDS = [
    "ANA-E1-ENTRY-SETUP-ANALYSIS",
    "ANA-E1-ENTRY-OPEN-DATA",
    "ANA-E1-API-READERRORDATA",
]
# Delphi 文档槽位(无 RTTI,RVA 未证实),与 generate_ledger slots 列表同序
DELPHI_SLOTS = [
    "Lin", "Ang", "Str", "Squ", "Par", "Rot", "Way",
    "Fla", "Dia", "LTB", "ATB", "STB", "LDA",
]
TAIL_IDS = ["ANA-UNK-ALG-ISO230-BODY", "ANA-E1-FLA-MOODY"]


def _api_id(ci_constant_name):
    # E1733A_CI_BIMAXREV -> ANA-E1-API-ANALYSIS-BIMAXREV
    return "ANA-E1-API-ANALYSIS-" + ci_constant_name.replace("E1733A_CI_", "")


ANA_ENTRY_IDS = (
    HEAD_IDS
    + [_api_id(ana.ANALYSIS_CI_MAP[ci]) for ci in sorted(ana.ANALYSIS_CI_MAP)]
    + [f"ANA-E1-STD-{i}" for i in sorted(ana.STANDARDS_MAP)]
    + [f"ANA-UNK-DELPHI-{s.upper()}DOC" for s in DELPHI_SLOTS]
    + TAIL_IDS
)


def test_ana_entry_ids_match_ledger_order_exactly():
    ledger_ids = ana.analysis_entry_ids()
    # 两侧均不允许重复
    assert len(ANA_ENTRY_IDS) == len(set(ANA_ENTRY_IDS))
    assert len(ledger_ids) == len(set(ledger_ids))
    # analysis 段由 build_ana_catalog 单函数顺序生成,故要求逐位顺序一致
    assert ANA_ENTRY_IDS == ledger_ids


def test_standards_map_matches_std_entries():
    # STANDARDS_MAP 固定 13 项,索引 0..12
    assert len(ana.STANDARDS_MAP) == 13
    assert set(ana.STANDARDS_MAP) == set(range(13))
    by_id = {e["identifier"]: e for e in ana.standard_entries()}
    assert len(by_id) == 13
    for idx, name in ana.STANDARDS_MAP.items():
        entry = by_id[f"ANA-E1-STD-{idx}"]
        assert entry["source_identifier"] == f"ANASETUP_STANDARD_CHOOSING={idx}"
        assert entry["status"] == "E1"
        assert entry["boundary"] == "remote_h_constant"
        assert entry["missing"] == f"standard={name}"


def test_analysis_ci_map_matches_api_entries():
    # CC_ANALYSIS(=66) 的 CI 选择子固定 28 项,索引 0..27
    assert len(ana.ANALYSIS_CI_MAP) == 28
    assert set(ana.ANALYSIS_CI_MAP) == set(range(28))
    by_id = {e["identifier"]: e for e in ana.analysis_entries()}
    api_ids_in_ledger = {
        i for i in by_id if i.startswith("ANA-E1-API-ANALYSIS-")
    }
    expected_api_ids = {_api_id(n) for n in ana.ANALYSIS_CI_MAP.values()}
    # ledger 中的 ANA-E1-API-ANALYSIS-* 与映射一一对应,不多不少
    assert api_ids_in_ledger == expected_api_ids
    for ci, name in ana.ANALYSIS_CI_MAP.items():
        entry = by_id[_api_id(name)]
        assert entry["source_identifier"] == f"CC_ANALYSIS=66 CI={ci}"
        assert entry["status"] == "E1"
        assert entry["boundary"] == "remote_h_constant"
    # 映射的 CI 索引与冻结的 Remote.h 常量清单交叉一致
    assert ana.verify_analysis_ci_map() == []


def test_unknown_entries_status_still_unknown():
    unknown = [
        e for e in ana.analysis_entries()
        if e["identifier"].startswith("ANA-UNK-")
    ]
    # 13 个 Delphi 文档槽 + ISO 230-2 计算体
    assert len(unknown) == 14
    for entry in unknown:
        assert entry["status"] == "unknown"
        assert entry["window_hash"] is None
    # Delphi 槽位辅助函数与 identifier/logical_slot 保持一致
    slots = ana.unknown_delphi_slots()
    assert len(slots) == 13
    for item in slots:
        slot = item["logical_slot"]
        assert slot in DELPHI_SLOTS
        assert item["identifier"] == f"ANA-UNK-DELPHI-{slot.upper()}DOC"
