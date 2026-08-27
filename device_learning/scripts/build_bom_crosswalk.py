#!/usr/bin/env python3
"""Crosswalk BOM components to HW catalog identifiers."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Hand-curated mapping: BOM ref_designator keywords → HW identifier
MAPPINGS = [
    (["FPGA", "SPARTAN", "XC3S200"], ["HW-001-FPGA-DEVICE", "HW-002-FPGA-PACKAGE"]),
    (["USB", "CY7C68013"], ["HW-003-USB-CONTROLLER", "HW-004-USB-PACKAGE", "HW-017-INTERFACE-USB"]),
    (["SRAM", "ISSI"], ["HW-023-MEMORY-SRAM"]),
    (["EEPROM", "24LC"], ["HW-012-EEPROM", "HW-013-EEPROM-CAPACITY"]),
    (["24.000M", "晶体", "crystal"], ["HW-014-CRYSTAL-USB"]),
    (["G6JU", "relay", "继电器"], ["HW-008-RELAY-ARRAY", "HW-009-RELAY-COUNT", "HW-010-RELAY-VOLTAGE"]),
    (["KS245"], ["HW-011-BUS-TRANSCEIVER"]),
    (["ADS127", "ADC"], ["HW-005-ADC-PRIMARY", "HW-006-ADC-COUNT", "HW-007-ADC-RESOLUTION"]),
    (["BNC", "coax", "同轴"], ["HW-016-INTERFACE-COAX"]),
    (["D-sub", "DSUB", "AMP"], ["HW-018-INTERFACE-DSUB"]),
    (["198755F", "revision"], ["HW-019-BOARD-REVISION"]),
    (["barcode", "serial", "条码"], ["HW-020-BOARD-SERIAL"]),
    (["470", "tantalum", "钽"], ["HW-022-POWER-TANTALUM"]),
    (["CE", "compliance"], ["HW-030-COMPLIANCE"]),
    (["COPYRIGHT", "2011"], ["HW-025-COPYRIGHT-YEAR"]),
    (["J600"], ["HW-031-CONNECTOR-J600"]),
    (["J603"], ["HW-032-CONNECTOR-J603"]),
]


def match_component(comp: dict) -> list[str]:
    blob = " ".join(
        [
            comp.get("ref_designator", ""),
            comp.get("part_marking", ""),
            comp.get("function", ""),
        ]
    ).upper()
    hits: list[str] = []
    for keys, ids in MAPPINGS:
        if any(k.upper() in blob for k in keys):
            hits.extend(ids)
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
        "boundary": "Keyword heuristic only; not a netlist",
    }
    out = ROOT / "manifests" / "bom_crosswalk.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"linked_count": meta["linked_count"]}, indent=2))


if __name__ == "__main__":
    main()
