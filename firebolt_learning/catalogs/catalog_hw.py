"""HW-* : 硬件拓扑标识（阶段 C）。照片默认远程索引，料号多 candidate。"""
from __future__ import annotations

from typing import Any

HW_ENTRIES: list[tuple[str, str, str, str, str]] = [
    (
        "HW-BRAND-NI",
        "PCB branded National Instruments",
        "confirmed",
        "photo_silkscreen",
        "NI logo / ni.com/patents / © 2024 on teardown photos",
    ),
    (
        "HW-USB-C",
        "USB Type-C host connector",
        "confirmed",
        "photo",
        "Visible on board edge",
    ),
    (
        "HW-FX3-CYUSB3014",
        "Cypress EZ-USB FX3 CYUSB3014",
        "confirmed",
        "photo_marking",
        "Matches firmware ThreadX ARM9 / FX3 strings",
    ),
    (
        "HW-FPGA-ARTIX7",
        "Xilinx Artix-7 FPGA present",
        "confirmed",
        "photo_and_bitstream",
        "Photo marking + IDCODE XC7A100T",
    ),
    (
        "HW-FPGA-XC7A100T",
        "FPGA device XC7A100T",
        "confirmed",
        "bitstream_idcode",
        "IDCODE 0x0362C093; some photo OCR may say 50T — binary wins",
    ),
    (
        "HW-ASSY-114365F",
        "Assembly label 114365F-01L/03L family",
        "candidate",
        "photo_label",
        "Multiple sticker variants across photos",
    ),
    (
        "HW-OEM-S2C",
        "Board-level S2C-SMT high-density connectors",
        "candidate",
        "photo",
        "Consistent with USB-6453 OEM 50-pin style interconnect",
    ),
    (
        "HW-ADC-ARRAY",
        "Repetitive multi-channel analog front-end array",
        "candidate",
        "photo_layout",
        "Supports 16-ADC architecture; MPN not confirmed",
    ),
    (
        "HW-ADC-MPN",
        "Exact ADC manufacturer part numbers",
        "unknown",
        "needs_photo_or_bom",
        "See OMISSIONS",
    ),
    (
        "HW-SYNC-LOCUS",
        "Sync locus is ADC array + FPGA, not FX3 ARM",
        "confirmed",
        "spec_plus_arch",
        "FX3 lacks sample/sync strings; SPEC requires shared convert clock",
    ),
]


def build_entries() -> list[dict[str, Any]]:
    return [
        {
            "identifier": i,
            "module": "hardware",
            "source_identifier": t,
            "status": s,
            "boundary": b,
            "note": n,
        }
        for i, t, s, b, n in HW_ENTRIES
    ]


def entry_ids() -> list[str]:
    return [e[0] for e in HW_ENTRIES]
