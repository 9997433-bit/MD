"""Acquisition catalog for E1733A static analysis.

边界：仅登记 Remote.h 常量、PE 导出符号与 import 旁证；
不推断 ProcessRawData 公式，不画 GUI→硬件 proven_bridge。
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
TRIG_IDS = ["ACQ-E1-TRIG-MANUAL", "ACQ-E1-TRIG-ENCODER", "ACQ-E1-TRIG-AUTO"]
UNK_IDS = ["ACQ-UNK-DELPHI-COLLECTDOC", "ACQ-UNK-PAUSE-RESUME", "ACQ-BRIDGE-GUI-TO-E1735A"]
ACQ_ENTRY_IDS = MEATYPE_IDS + CMD_IDS + TRIG_IDS + UNK_IDS  # DLL 行动态追加


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


def meatype_ids() -> list[str]:
    return [e["identifier"] for e in acquisition_entries() if e["identifier"].startswith("ACQ-E1-MEATYPE-")]


def dll_export_ids() -> list[str]:
    return [e["identifier"] for e in acquisition_entries() if e["identifier"].startswith("ACQ-E1-DLL-") or e["identifier"].startswith("ACQ-E1-CORE-")]
