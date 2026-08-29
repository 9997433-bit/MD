#!/usr/bin/env python3
"""Deep static metadata for Firebolt FPGA configuration image (learning package)."""
from __future__ import annotations

import json
import math
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "niusbFireboltFPGA.cfg"
OUT = ROOT / "manifests" / "bitstream_deep.json"

REG = {
    0: "CRC",
    1: "FAR",
    2: "FDRI",
    3: "FDRO",
    4: "CMD",
    5: "CTL0",
    6: "MASK",
    7: "STAT",
    9: "COR0",
    12: "IDCODE",
    14: "COR1",
    16: "WBSTAR",
    17: "TIMER",
    24: "CTL1",
}


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def main() -> None:
    data = FW.read_bytes()
    lead = 0
    while lead < len(data) and data[lead] == 0xFF:
        lead += 1
    sync = data.find(b"\xaa\x99\x55\x66")
    idcode = None
    packet_stats: dict[str, int] = Counter()
    fdri_segments: list[dict] = []

    if sync >= 0:
        i = sync + 4
        while i + 4 <= len(data):
            w = struct.unpack_from(">I", data, i)[0]
            typ = (w >> 29) & 7
            if typ == 1:
                op = (w >> 27) & 3
                reg = (w >> 13) & 0x3FFF
                cnt = w & 0x7FF
                name = REG.get(reg, str(reg))
                packet_stats[f"T1_op{op}_{name}"] += 1
                i += 4
                if op == 2 and cnt == 1 and i + 4 <= len(data):
                    val = struct.unpack_from(">I", data, i)[0]
                    if reg == 12:
                        idcode = val
                    i += 4
                elif op == 2 and 0 < cnt < 0x7FF:
                    i += 4 * cnt
                elif op == 2 and cnt == 0:
                    pass
            elif typ == 2:
                cnt = w & 0x7FFFFFF
                packet_stats["T2_FDRI_like"] += 1
                fdri_segments.append(
                    {"offset": i, "word_count": cnt, "byte_count": cnt * 4}
                )
                i += 4 + 4 * cnt
            else:
                packet_stats[f"T{typ}_other"] += 1
                i += 4
                if packet_stats[f"T{typ}_other"] > 10000:
                    break

    out = {
        "path": str(FW.relative_to(ROOT)),
        "size": len(data),
        "entropy": round(entropy(data), 3),
        "leading_ff": lead,
        "bus_width_detect_hex": data[0x20:0x30].hex() if len(data) > 0x30 else None,
        "sync_offset": sync,
        "idcode": f"0x{idcode:08X}" if idcode is not None else None,
        "device": "XC7A100T" if idcode == 0x0362C093 else None,
        "packet_stats": dict(packet_stats),
        "fdri_segments": fdri_segments,
        "fdri_segment_count": len(fdri_segments),
        "boundary_note": (
            "Device/carrier confirmed via IDCODE. Sample-clock tree, bank/AIConv HDL, "
            "and FIFO packing remain unknown without netlist or lab; do not upgrade "
            "BIT-SYNC-CLOCK-TREE / BIT-BANK-AICONV from this metadata alone."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "idcode": out["idcode"], "fdri": len(fdri_segments), "size": len(data)}))


if __name__ == "__main__":
    main()
