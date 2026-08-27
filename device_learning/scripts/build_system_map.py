#!/usr/bin/env python3
"""Build cross-layer system map from manifests and catalogs."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    bom = json.loads((ROOT / "manifests" / "hardware_bom.json").read_text(encoding="utf-8"))
    pins = json.loads((ROOT / "manifests" / "pin_hypothesis.json").read_text(encoding="utf-8"))
    frame = json.loads((ROOT / "manifests" / "frame_summary.json").read_text(encoding="utf-8"))

    nodes = [
        {
            "id": "NODE-IN",
            "layer": "hw",
            "name": "Analog input (coax)",
            "evidence": ["HW-016-INTERFACE-COAX", "SIG-001-PATH-IN"],
            "status": "confirmed",
        },
        {
            "id": "NODE-RELAY",
            "layer": "hw",
            "name": "Relay matrix",
            "evidence": ["HW-008-RELAY-ARRAY", "SIG-002-RELAY-MATRIX", "BRG-013"],
            "status": "candidate",
        },
        {
            "id": "NODE-ADC",
            "layer": "hw",
            "name": "24-bit ADC",
            "evidence": ["HW-005-ADC-PRIMARY", "SIG-003-PATH-ADC", "REF-ADC-SPI-DOUT"],
            "status": "candidate",
        },
        {
            "id": "NODE-FPGA",
            "layer": "bit",
            "name": "FPGA fabric",
            "evidence": ["HW-001-FPGA-DEVICE", "BIT-IDCODE", "BIT-FDRI-WORD-COUNT"],
            "status": "confirmed",
        },
        {
            "id": "NODE-USB-CTL",
            "layer": "hw",
            "name": "USB controller",
            "evidence": ["HW-003-USB-CONTROLLER", "REF-USB-SLAVE-FIFO-SLRD"],
            "status": "confirmed",
        },
        {
            "id": "NODE-HOST",
            "layer": "usb",
            "name": "Host PC",
            "evidence": ["PROTO-001-USB-DESCRIPTORS"],
            "status": "not_started",
        },
    ]
    edges = [
        {"from": "NODE-IN", "to": "NODE-RELAY", "type": "analog", "status": "candidate"},
        {"from": "NODE-RELAY", "to": "NODE-ADC", "type": "analog", "status": "candidate"},
        {"from": "NODE-ADC", "to": "NODE-FPGA", "type": "digital", "status": "hypothesis"},
        {"from": "NODE-FPGA", "to": "NODE-USB-CTL", "type": "slave_fifo", "status": "hypothesis"},
        {"from": "NODE-USB-CTL", "to": "NODE-HOST", "type": "usb2", "status": "not_started"},
    ]
    bit_facts = {
        "idcode": frame.get("packet_stream", {}).get("registers", {}).get("IDCODE", {}),
        "frame_analysis": frame.get("frame_analysis", {}),
        "cmd_sequence": frame.get("packet_stream", {}).get("cmd_sequence", []),
    }
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "bit_facts": bit_facts,
        "bom_component_count": len(bom.get("components", [])),
        "pin_bridge_count": pins.get("count", len(pins.get("bridges", []))),
    }
    out = ROOT / "manifests" / "system_map.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"system_map: {len(nodes)} nodes, {len(edges)} edges")


if __name__ == "__main__":
    main()
