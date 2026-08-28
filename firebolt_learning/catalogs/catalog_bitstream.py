"""BIT-* : FPGA bitstream 载体与边界（阶段 E）。"""
from __future__ import annotations

from typing import Any

BIT_ENTRIES: list[tuple[str, str, str, str, str]] = [
    (
        "BIT-FMT-BIN",
        "Raw .bin style (FF pad + bus width detect + sync)",
        "confirmed",
        "firmware_bytes",
        "No Xilinx .bit ASCII header",
    ),
    (
        "BIT-SYNC-WORD",
        "Sync word AA995566 present",
        "confirmed",
        "firmware_bytes",
        "7-series bitstream",
    ),
    (
        "BIT-IDCODE",
        "IDCODE 0x0362C093 = XC7A100T",
        "confirmed",
        "bitstream_packet",
        "Type1 write IDCODE",
    ),
    (
        "BIT-COMPRESSED",
        "Compressed FDRI segments (~1.60 MiB)",
        "candidate",
        "size_heuristic",
        "Uncompressed 7A100T ~3.8 MiB typical",
    ),
    (
        "BIT-SYNC-CLOCK-TREE",
        "Sample-clock / multi-ADC convert tree in fabric",
        "unknown",
        "needs_netlist",
        "OMISSIONS — sync logic locus asserted by SPEC+arch only",
    ),
    (
        "BIT-BANK-AICONV",
        "Bank switch and AIConv timer implementation",
        "unknown",
        "needs_netlist_or_lab",
        "OMISSIONS",
    ),
    (
        "BIT-FIFO-LOGIC",
        "AI FIFO sizing / packing in fabric",
        "unknown",
        "needs_netlist",
        "SPEC gives 8191 samples; HDL unknown",
    ),
]


def build_entries() -> list[dict[str, Any]]:
    return [
        {
            "identifier": i,
            "module": "bitstream",
            "source_identifier": t,
            "status": s,
            "boundary": b,
            "note": n,
        }
        for i, t, s, b, n in BIT_ENTRIES
    ]


def entry_ids() -> list[str]:
    return [e[0] for e in BIT_ENTRIES]
