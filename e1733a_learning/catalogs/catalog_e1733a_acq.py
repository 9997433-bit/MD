"""Acquisition catalog for E1733A static analysis.

边界：仅登记 EvidenceLedger.json 中 catalogs.acquisition 一段的条目——
Remote.h 常量（MEATYPE / CMD / TRIG）、E1735A 与 E1735ACore 的 PE 导出
符号、以及 import 旁证 / 未证实条目（ACQ-UNK-* / ACQ-BRIDGE-*）。
不推断 ProcessRawData 公式，不画 GUI→硬件 proven_bridge；
数据以 EvidenceLedger.json 为唯一权威来源，本模块只提供只读访问。

TRIG-STR candidate 条目说明
---------------------------
ACQ-E1-TRIG-STR-* 四条（TARGETWIN / DWELL / ENCRES / EPTIMEOUT）对应
straightness（直线度）测量下 Remote.h 里出现的触发/采样设置项。它们的
status 为 ``candidate`` 而非 ``E1``：目前仅有 UI 字符串锚点（见
manifests/english_string_gaps.json 的 MEASETUP_TRIGWND_* 等 ITEMTEXT），
尚未在反编译中定位到对应的常量赋值或触发公式，因此只作为“候选”登记，
不推断其数值语义、单位或与硬件采样的绑定关系。待反编译证据补齐后方可
升级为 E1。这些条目的 boundary 仍标为 ``remote_h_constant``（字符串出处
在 Remote.h 语境），与已证实的 TRIG-MANUAL/ENCODER/AUTO 区分仅在 status。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

MEATYPE_IDS = [f"ACQ-E1-MEATYPE-{n}" for n in (
    "LINEAR", "ANGULAR", "STR", "SQU", "PAR", "ROT", "WAY", "FLA", "DIA", "LTB", "ATB", "STB", "DUAL"
)]
CMD_IDS = [
    "ACQ-E1-CMD-START", "ACQ-E1-CMD-RECORD", "ACQ-E1-CMD-RESET", "ACQ-E1-CMD-STOP",
]
TRIG_IDS = [
    "ACQ-E1-TRIG-MANUAL", "ACQ-E1-TRIG-ENCODER", "ACQ-E1-TRIG-AUTO",
    "ACQ-E1-TRIG-STR-TARGETWIN", "ACQ-E1-TRIG-STR-DWELL",
    "ACQ-E1-TRIG-STR-ENCRES", "ACQ-E1-TRIG-STR-EPTIMEOUT",
]
# E1735A.dll 导出符号
DLL_IDS = [f"ACQ-E1-DLL-E1735A_{n}" for n in (
    "BlinkLED", "GetAllRevisions", "GetOptics", "GetParameter", "GetSampleTriggers",
    "QueryTBStatus", "ReadAQB", "ReadAllSamples", "ReadBeamStrength", "ReadButtonClicked",
    "ReadDeviceCount", "ReadLastError", "ReadLastTimeStamp", "ReadLastTrigger",
    "ReadSample", "ReadSampleAndAQB", "ReadSampleCount", "ReadSerialNo", "ReadTimerSamples",
    "RefreshDevice", "RefreshStatus", "ResetDevice", "SelectDevice", "SetExternalPolarity",
    "SetOptics", "SetParameter", "SetSampleTriggers", "SetupAQB", "SetupTimer",
    "SpecifyDevice", "StartExternalSampling", "StartTimer", "StopExternalSampling", "StopTimer",
)] + [
    "ACQ-E1-DLL-TMethodImplementationIntercept",
    "ACQ-E1-DLL-__dbk_fcall_wrapper",
    "ACQ-E1-DLL-dbkFCallWrapperAddr",
]
# E1735ACore.dll 导出符号（含 Delphi 运行时导出）
CORE_IDS = [f"ACQ-E1-CORE-E1735ACore_{n}" for n in (
    "CloseHandles", "ConfigureCard", "ControlLEDs", "GetCardHandle", "GetCardNumber",
    "GetDLLRevision", "GetDriverRevision", "GetLastError", "GetRegRevision",
    "ProcessRawData", "ReadCardInfo", "ReadRawData", "ReadRegisters",
    "SearchCards", "WriteRegisters",
)] + [
    "ACQ-E1-CORE-TMethodImplementationIntercept",
    "ACQ-E1-CORE-__dbk_fcall_wrapper",
    "ACQ-E1-CORE-dbkFCallWrapperAddr",
]
UNK_IDS = ["ACQ-UNK-DELPHI-COLLECTDOC", "ACQ-UNK-PAUSE-RESUME", "ACQ-BRIDGE-GUI-TO-E1735A"]
# 顺序与 EvidenceLedger.json 中 acquisition 段一致
ACQ_ENTRY_IDS = MEATYPE_IDS + CMD_IDS + TRIG_IDS + DLL_IDS + CORE_IDS + UNK_IDS


def load_ledger() -> dict[str, Any]:
    return json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))


def acquisition_entries() -> list[dict[str, Any]]:
    return load_ledger()["catalogs"]["acquisition"]


def get_entry(identifier: str) -> dict[str, Any] | None:
    for e in acquisition_entries():
        if e["identifier"] == identifier:
            return e
    return None


def entries_by_status(status: str) -> list[dict[str, Any]]:
    return [e for e in acquisition_entries() if e["status"] == status]


def entries_by_boundary(boundary: str) -> list[dict[str, Any]]:
    """按 ledger 的 ``boundary`` 字段过滤（如 remote_h_constant /
    pe_export_symbol / pe_import_only / no_rtti / export_absent）。"""
    return [e for e in acquisition_entries() if e.get("boundary") == boundary]


def meatype_ids() -> list[str]:
    return [e["identifier"] for e in acquisition_entries() if e["identifier"].startswith("ACQ-E1-MEATYPE-")]


def cmd_ids() -> list[str]:
    return [e["identifier"] for e in acquisition_entries() if e["identifier"].startswith("ACQ-E1-CMD-")]


def trig_ids() -> list[str]:
    return [e["identifier"] for e in acquisition_entries() if e["identifier"].startswith("ACQ-E1-TRIG-")]


def trig_str_candidate_ids() -> list[str]:
    """straightness 触发候选条目（ACQ-E1-TRIG-STR-*，status=candidate）。"""
    return [
        e["identifier"]
        for e in acquisition_entries()
        if e["identifier"].startswith("ACQ-E1-TRIG-STR-")
    ]


def dll_export_ids() -> list[str]:
    return [e["identifier"] for e in acquisition_entries() if e["identifier"].startswith("ACQ-E1-DLL-") or e["identifier"].startswith("ACQ-E1-CORE-")]
