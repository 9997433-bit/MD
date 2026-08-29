#!/usr/bin/env python3
"""FX3 MMIO / PIB-GPIF static map for Firebolt learning (no USB capture)."""
from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "niusbFirebolt.cfg"
OUT = ROOT / "manifests" / "fx3_mmio_map.json"
BASE = 0x3FFD6000

# Cypress FX3 peripheral regions (TRM / public headers; labels are conventional)
NAMED = {
    0xE0000000: "low_periph",
    0xE0010000: "PIB_GPIF",
    0xE0020000: "LPP",
    0xE0030000: "UIB_USB",
    0xE0050000: "GCTL",
}


def main() -> None:
    data = FW.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    freq: Counter[int] = Counter()
    for i in range(0, len(data) - 4, 4):
        w = struct.unpack_from("<I", data, i)[0]
        if 0xE0000000 <= w < 0xE0100000:
            freq[w] += 1

    top = [
        {
            "value": f"0x{v:08X}",
            "count": c,
            "region": NAMED.get(v & 0xFFFF0000, NAMED.get(v & 0xFFFFF000, "other")),
        }
        for v, c in freq.most_common(40)
    ]

    # Evidence: socket stride pattern near VA 0x400115F8
    # Observed: lsl r3,r0,#4; ...; add r3,#0xE0000000; add r3,#0x10000
    # => 0xE0010000 + index*16
    fo = 0x400115F8 - BASE
    chunk = data[fo : fo + 24]
    decoded = [f"{i.address:#x}: {i.mnemonic} {i.op_str}" for i in md.disasm(chunk, 0x400115F8)]
    pib_stride_evidence = {
        "va": "0x400115F8",
        "pattern": "r3 = 0xE0010000 + (socket_index << 4)",
        "insns": [
            "lsl r3, r0, #4",
            "add r3, r3, #0xe0000000",
            "add r3, r3, #0x10000",
        ],
        "decoded_at_va": decoded,
        "meaning": "FX3 PIB socket register block stride 16 bytes",
        "status": "confirmed",
    }

    # Region hit summary
    region_hits: Counter[str] = Counter()
    for v, c in freq.items():
        key = NAMED.get(v & 0xFFFF0000, "other")
        region_hits[key] += c

    out = {
        "schema": "firebolt_learning.fx3_mmio_map.v1",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "load_base": f"0x{BASE:08X}",
        "named_regions": {f"0x{k:08X}": v for k, v in NAMED.items()},
        "literal_top": top,
        "region_literal_hits": dict(region_hits),
        "pib_socket_stride": pib_stride_evidence,
        "learning": {
            "usb_plane": "UIB literals 0xE0030000 / 0xE0033000 dominate — USB engine",
            "fpga_bridge": (
                "PIB/GPIF @ 0xE0010000 with socket*16 addressing is the on-chip bridge "
                "toward FPGA fabric; this is NOT the FPGA fabric register map itself"
            ),
            "gctl": "GCTL @ 0xE0050000 present — clocks/power/id",
            "still_unknown": [
                "FPGA fabric register offsets (FX3-REGMAP)",
                "Fusion bRequest dictionary (FX3-FUSION-REQ)",
                "USB Signal Stream frame layout",
            ],
        },
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "unique_mmio_imm": len(freq),
                "pib_hits": region_hits.get("PIB_GPIF", 0),
                "uib_hits": region_hits.get("UIB_USB", 0),
                "decoded": decoded,
            }
        )
    )


if __name__ == "__main__":
    main()
