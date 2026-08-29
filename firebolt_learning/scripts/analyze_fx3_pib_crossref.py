#!/usr/bin/env python3
"""Cross-reference Firebolt FX3 immediates with public Cypress PIB/GPIF map."""
from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "niusbFirebolt.cfg"
OUT = ROOT / "manifests" / "fx3_pib_crossref.json"

# From public Cypress FX3 SDK pib_regs.h / gpif_regs.h (nickdademo/cypress-fx3-sdk-linux)
CYPRESS_MAP = {
    0xE0010000: {"name": "PIB_CONFIG", "group": "pib_core"},
    0xE0010004: {"name": "PIB_INTR", "group": "pib_core"},
    0xE0010008: {"name": "PIB_INTR_MASK", "group": "pib_core"},
    0xE001000C: {"name": "PIB_CLOCK_DETECT", "group": "pib_core"},
    0xE0010010: {"name": "PIB_RD_MAILBOX0", "group": "pib_core"},
    0xE0010018: {"name": "PIB_WR_MAILBOX0", "group": "pib_core"},
    0xE0014000: {"name": "GPIF_CONFIG", "group": "gpif"},
    0xE0014004: {"name": "GPIF_BUS_CONFIG", "group": "gpif"},
    0xE00140FC: {"name": "GPIF_THREAD_CONFIG[0]", "group": "gpif"},
    0xE0014118: {"name": "GPIF_WAVEFORM_CTRL_STAT", "group": "gpif"},
    0xE0017E00: {"name": "PP_ID", "group": "pp_mode"},
    0xE0017E34: {"name": "PP_WR_MAILBOX0", "group": "pp_mode"},
    0xE0017E3C: {"name": "PP_MMIO_ADDR", "group": "pp_mode", "note": "fabric MMIO window addr"},
    0xE0017E40: {"name": "PP_MMIO_DATA", "group": "pp_mode", "note": "fabric MMIO window data"},
    0xE0017E44: {"name": "PP_MMIO", "group": "pp_mode"},
    0xE0017F00: {"name": "PIB_ID", "group": "pib_id"},
    0xE0017F04: {"name": "PIB_POWER", "group": "pib_id"},
    0xE0018000: {"name": "PIB_SCK0_DSCR", "group": "sockets", "note": "socket[n] base = 0xE0018000 + n*0x80"},
    0xE0018010: {"name": "PIB_SCK0_INTR", "group": "sockets"},
}


def count_imm(data: bytes, value: int) -> int:
    ptr = struct.pack("<I", value)
    n = 0
    start = 0
    while True:
        j = data.find(ptr, start)
        if j < 0:
            break
        if j % 4 == 0:
            n += 1
        start = j + 1
    return n


def main() -> None:
    data = FW.read_bytes()
    hits = []
    for addr, meta in sorted(CYPRESS_MAP.items()):
        c = count_imm(data, addr)
        hits.append(
            {
                "address": f"0x{addr:08X}",
                "count": c,
                "present": c > 0,
                **meta,
            }
        )

    # All E001xxxx frequency for context
    freq: Counter[int] = Counter()
    for i in range(0, len(data) - 4, 4):
        w = struct.unpack_from("<I", data, i)[0]
        if 0xE0010000 <= w < 0xE0020000:
            freq[w] += 1

    e0011000_note = (
        "0xE0011000 lies inside pib_regs.h rsrvd0[] gap (between core +0x28 and "
        "GPIF @0xE0014000). Firmware writes here, but public header gives no field names — "
        "keep semantics candidate/unknown; do not equate to GPIF_CONFIG or socket[]."
    )

    out = {
        "schema": "firebolt_learning.fx3_pib_crossref.v1",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "source": {
            "header": "Cypress FX3 SDK pib_regs.h / gpif_regs.h",
            "reference_repo": "https://github.com/nickdademo/cypress-fx3-sdk-linux",
        },
        "official_layout_summary": {
            "PIB_BASE": "0xE0010000",
            "GPIF_REGS": "0xE0014000",
            "PP_MAILBOX_MMIO": "0xE0017E34 .. 0xE0017E50",
            "SOCKET_ARRAY": "0xE0018000 + n*0x80 (32 sockets)",
            "socket_stride_bytes": 128,
        },
        "named_literal_hits": hits,
        "present_groups": sorted(
            {h["group"] for h in hits if h["present"]}
        ),
        "absent_but_important": [
            h for h in hits if (not h["present"]) and h["group"] in ("pp_mode", "gpif")
        ],
        "e0011000_clarification": {
            "address": "0xE0011000",
            "firmware_literal_count": freq.get(0xE0011000, 0),
            "note": e0011000_note,
            "status": "candidate",
        },
        "socket_stride_clarification": {
            "prior_claim": "0xE0010000 + index<<4 (16-byte)",
            "official_socket_stride": "0xE0018000 + index*0x80 (128-byte)",
            "resolution": (
                "Keep both observations: <<4 pattern exists in disassembly against 0xE0010000; "
                "official DMA socket registers use *0x80 at 0xE0018000 (literal present). "
                "Do not collapse them into one map without more RE."
            ),
            "status": "candidate",
        },
        "pp_mmio_path": {
            "importance": "PP_MMIO_ADDR/DATA are the public PP-mode window into external/FPGA space",
            "absolute_literals_in_image": False,
            "implication": (
                "Fabric register access may use PIB base pointer + 0x7E3C/0x7E40 offsets, "
                "GPIF ingress/egress regs, or a non-PP path — still unknown without deeper RE/capture"
            ),
            "status": "unknown",
        },
        "top_e001_literals": [
            {"address": f"0x{a:08X}", "count": c} for a, c in freq.most_common(20)
        ],
        "learning": {
            "confirmed": [
                "Firmware links Cypress PIB @0xE0010000, GPIF @0xE0014000, sockets @0xE0018000",
                "FPGA data plane remains GPIF/PIB — sync timebase still not on ARM",
            ],
            "refined": [
                "0xE0011000 init block is not a named public GPIF struct — demote over-specific naming",
                "Official socket stride is 128B; prior 16B claim is a separate pattern",
            ],
            "still_unknown": [
                "PP_MMIO fabric register dictionary",
                "Which PIB sockets carry AI sample stream",
                "Fusion bRequest → PIB/GPIF programming sequence",
            ],
        },
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    present = sum(1 for h in hits if h["present"])
    print(json.dumps({"ok": True, "named_present": present, "named_total": len(hits), "e001_unique": len(freq)}))


if __name__ == "__main__":
    main()
