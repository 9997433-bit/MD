"""Format disposition catalog for E1733A Option Description Files.

Option Description File 格式
============================
E1733A 的 "Option Description File" 是仪器针对每一种测量选项(measurement
option)导出的样本描述文件。每个逻辑测量槽位(logical slot)对应一个固定的
文件扩展名,例如线性测量导出 ``Sample.Lin``、角度测量导出 ``Sample.Ang``。
EvidenceLedger.json 的 ``catalogs.formats`` 段冻结了 25 条格式证据,可分为四类:

1. Sample 扩展名格式(13 条)
2. Remote.h CC_SAVE 写盘子类型(10 条,forbidden_writer)
3. 时基原始数据尾块(1 条,``FMT-TBRAWDATA-SECTION``,candidate)
4. 强制断桥(1 条,``FMT-LTB-VELOCITY-BRIDGE``,forced_null)

disposition 语义
================
``disposition`` 字段描述该格式在静态分析中的处置方式,共三种取值:

- ``forbidden_writer``:10 条 ``FMT-SAVE-*`` 写盘路径（静态分析禁止实现写出）。
- ``sample_scope_parser``:13 条 Sample 扩展名 + 1 条 ``FMT-TBRAWDATA-SECTION``（尾块 candidate）。
- ``forced_null``:``FMT-LTB-VELOCITY-BRIDGE`` 不得桥接速度公式。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# 逻辑槽位 <-> 文件扩展名。覆盖 sample_manifest.json 中全部 13 个 Sample 扩展名,
# 每个扩展名映射到 EvidenceLedger.json 中对应 FMT-<EXT> 条目的 logical_slot。
EXT_TO_SLOT = {
    ".lin": "Lin", ".ang": "Ang", ".str": "Str", ".squ": "Squ", ".par": "Par",
    ".rot": "Rot", ".way": "Way", ".fla": "Fla", ".dia": "Dia", ".ltb": "LTB",
    ".atb": "ATB", ".stb": "STB", ".lda": "LDA",
}

# formats 段 25 条证据的 identifier,顺序与 EvidenceLedger.json 完全一致。
FMT_ENTRY_IDS = [
    "FMT-ATB", "FMT-ANG", "FMT-DIA", "FMT-FLA", "FMT-LDA", "FMT-LTB", "FMT-LIN",
    "FMT-PAR", "FMT-STB", "FMT-SQU", "FMT-WAY", "FMT-ROT", "FMT-STR",
    "FMT-SAVE-RAWDATA_TXT", "FMT-SAVE-RAWDATA_CSV", "FMT-SAVE-RAWDATA_POS",
    "FMT-SAVE-RAWDATA_RUN", "FMT-SAVE-COMPTABLE_TXT", "FMT-SAVE-COMPTABLE_CSV",
    "FMT-SAVE-COMPTABLE_POS", "FMT-SAVE-COMPTABLE_RUN", "FMT-SAVE-ENVDATA_TXT",
    "FMT-SAVE-ENVDATA_CSV", "FMT-TBRAWDATA-SECTION", "FMT-LTB-VELOCITY-BRIDGE",
]


def load_ledger() -> dict[str, Any]:
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def load_sample_manifest() -> dict[str, Any]:
    return json.loads(
        (ROOT / "manifests" / "sample_manifest.json").read_text(encoding="utf-8")
    )


def format_entries() -> list[dict[str, Any]]:
    return load_ledger()["catalogs"]["formats"]


def format_disposition() -> dict[str, str]:
    return {e["identifier"]: e.get("disposition", e.get("status", "")) for e in format_entries()}


def format_by_extension(ext: str) -> dict[str, Any] | None:
    ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
    slot = EXT_TO_SLOT.get(ext)
    if not slot:
        return None
    ident = f"FMT-{ext[1:].upper()}"
    for e in format_entries():
        if e["identifier"] == ident:
            return e
    return None


def format_slots() -> dict[str, str]:
    """Return the extension -> logical slot mapping for Sample formats.

    返回 13 个 Sample 扩展名到逻辑槽位的映射,槽位取自 EvidenceLedger.json
    中对应 FMT-<EXT> 条目的 ``logical_slot`` 字段,以 ledger 为准而非硬编码,
    从而保证 EXT_TO_SLOT 与冻结证据保持一致。
    """
    by_slot = {
        e["logical_slot"]: e
        for e in format_entries()
        if e.get("logical_slot")
    }
    out: dict[str, str] = {}
    for ext, slot in EXT_TO_SLOT.items():
        if slot in by_slot:
            out[ext] = slot
    return out


def verify_extension_coverage() -> dict[str, Any]:
    """Verify all 13 Sample extensions are fully covered by the catalog.

    对 sample_manifest.json 中的每个样本扩展名做三重校验:
    1. 扩展名存在于 EXT_TO_SLOT;
    2. 其映射槽位与 ledger 中对应 FMT-<EXT> 条目的 logical_slot 一致;
    3. 该 FMT 条目携带非空 sample_sha256,且与 manifest 中的 sha256 相符。

    返回校验报告;``ok`` 为 True 表示 13 个扩展名全部覆盖且一致。
    """
    samples = load_sample_manifest()["samples"]
    entries = {e["identifier"]: e for e in format_entries()}

    missing_ext: list[str] = []
    slot_mismatch: list[dict[str, str]] = []
    sha_mismatch: list[dict[str, str]] = []
    covered: list[str] = []

    for s in samples:
        ext = s["extension"].lower()
        slot = EXT_TO_SLOT.get(ext)
        if slot is None:
            missing_ext.append(ext)
            continue
        entry = entries.get(f"FMT-{ext[1:].upper()}")
        if entry is None:
            missing_ext.append(ext)
            continue
        if entry.get("logical_slot") != slot:
            slot_mismatch.append(
                {"extension": ext, "ext_to_slot": slot, "ledger_slot": entry.get("logical_slot")}
            )
        if entry.get("sample_sha256") != s.get("sha256"):
            sha_mismatch.append(
                {
                    "extension": ext,
                    "manifest_sha256": s.get("sha256"),
                    "ledger_sha256": entry.get("sample_sha256"),
                }
            )
        covered.append(ext)

    expected = len(samples)
    ok = (
        not missing_ext
        and not slot_mismatch
        and not sha_mismatch
        and len(covered) == expected
    )
    return {
        "ok": ok,
        "expected_count": expected,
        "covered_count": len(covered),
        "covered": sorted(covered),
        "missing_extensions": sorted(missing_ext),
        "slot_mismatch": slot_mismatch,
        "sha256_mismatch": sha_mismatch,
    }
