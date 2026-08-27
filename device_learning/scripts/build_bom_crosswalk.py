#!/usr/bin/env python3
"""Crosswalk BOM components to HW catalog identifiers."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Match only on specified fields to avoid false positives from location prose in `function`.
RULES: list[dict] = [
    {"keys": ["SPARTAN", "XC3S200"], "fields": ["marking"], "ids": ["HW-001-FPGA-DEVICE", "HW-002-FPGA-PACKAGE"]},
    {"keys": ["CY7C68013"], "fields": ["marking", "ref"], "ids": ["HW-003-USB-CONTROLLER", "HW-004-USB-PACKAGE"]},
    {"keys": ["USB-B", "USB B"], "fields": ["marking", "ref", "function"], "ids": ["HW-017-INTERFACE-USB"]},
    {"keys": ["ISSI", "IS62WV"], "fields": ["marking", "ref"], "ids": ["HW-023-MEMORY-SRAM"]},
    {"keys": ["24LC", "EEPROM"], "fields": ["marking", "ref"], "ids": ["HW-012-EEPROM", "HW-013-EEPROM-CAPACITY"]},
    {"keys": ["24.000M"], "fields": ["marking", "ref"], "ids": ["HW-014-CRYSTAL-USB"]},
    {"keys": ["G6JU"], "fields": ["marking", "ref"], "ids": ["HW-008-RELAY-ARRAY", "HW-009-RELAY-COUNT", "HW-010-RELAY-VOLTAGE"]},
    {"keys": ["KS245"], "fields": ["marking", "ref"], "ids": ["HW-011-BUS-TRANSCEIVER"]},
    {"keys": ["ADS127"], "fields": ["marking", "ref"], "ids": ["HW-005-ADC-PRIMARY", "HW-006-ADC-COUNT", "HW-007-ADC-RESOLUTION"]},
    {"keys": ["BNC", "同轴"], "fields": ["marking", "ref", "function"], "ids": ["HW-016-INTERFACE-COAX"]},
    {"keys": ["D-SUB", "D-SUB", "AMP"], "fields": ["marking", "ref", "function"], "ids": ["HW-018-INTERFACE-DSUB"]},
    {"keys": ["198755F"], "fields": ["marking", "ref"], "ids": ["HW-019-BOARD-REVISION"]},
    {"keys": ["2489960", "条码"], "fields": ["marking", "ref"], "ids": ["HW-020-BOARD-SERIAL"]},
    {"keys": ["477A", "470"], "fields": ["marking"], "ids": ["HW-022-POWER-TANTALUM"]},
    {"keys": ["CE 标志", "CE标志"], "fields": ["marking", "function"], "ids": ["HW-030-COMPLIANCE"]},
    {"keys": ["COPYRIGHT 2011"], "fields": ["marking", "function"], "ids": ["HW-025-COPYRIGHT-YEAR"]},
    {"keys": ["J600"], "fields": ["ref", "marking"], "ids": ["HW-031-CONNECTOR-J600"]},
    {"keys": ["J603"], "fields": ["ref", "marking"], "ids": ["HW-032-CONNECTOR-J603"]},
]


def _field_text(comp: dict, field: str) -> str:
    if field == "ref":
        return comp.get("ref_designator", "")
    if field == "marking":
        return comp.get("part_marking", "")
    return comp.get("function", "")


def match_component(comp: dict) -> list[str]:
    hits: list[str] = []
    for rule in RULES:
        for field in rule["fields"]:
            blob = _field_text(comp, field).upper()
            if blob and any(k.upper() in blob for k in rule["keys"]):
                hits.extend(rule["ids"])
                break
    return sorted(set(hits))


def main() -> None:
    bom = json.loads((ROOT / "manifests" / "hardware_bom.json").read_text(encoding="utf-8"))
    links = []
    for comp in bom.get("components", []):
        hw_ids = match_component(comp)
        if hw_ids:
            links.append(
                {
                    "ref_designator": comp.get("ref_designator"),
                    "part_marking": comp.get("part_marking", "")[:60],
                    "hw_identifiers": hw_ids,
                    "bom_status": comp.get("status"),
                }
            )

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "component_count": len(bom.get("components", [])),
        "linked_count": len(links),
        "links": links,
        "boundary": "Keyword heuristic on ref/marking only; not a netlist",
    }
    out = ROOT / "manifests" / "bom_crosswalk.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"linked_count": meta["linked_count"]}, indent=2))


if __name__ == "__main__":
    main()
