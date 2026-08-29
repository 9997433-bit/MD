"""SPEC-* : USB-6453 规格书驱动的同步采集行为模型（阶段 B）。

边界：只登记规格语义，不推断 FPGA/FX3 寄存器实现。
权威来源：NI USB-6453 Specifications（16 ADC / simultaneous / bank / FIFO）。
"""
from __future__ import annotations

from typing import Any

# (id, title, status, boundary, note)
SPEC_ENTRIES: list[tuple[str, str, str, str, str]] = [
    (
        "SPEC-PRODUCT-USB-6453",
        "Product is NI USB-6453 mioDAQ (Firebolt)",
        "confirmed",
        "spec_and_usb_pid",
        "32 SE / 16 DIFF AI, 4 AO, 16 DIO; community maps PID 0x7B44 to Firebolt",
    ),
    (
        "SPEC-ADC-16",
        "Sixteen physical ADCs",
        "confirmed",
        "spec_sheet",
        "Number of ADC = 16",
    ),
    (
        "SPEC-SIM-MAX-16CH",
        "Up to 16 channels truly simultaneous",
        "confirmed",
        "spec_sheet",
        "Simultaneous sampling channels: up to 16",
    ),
    (
        "SPEC-SIM-1MS",
        "1 MS/s/ch for full simultaneous cases",
        "confirmed",
        "spec_sheet",
        "All 16 DIFF or up to 16 SE at 1 MS/s/ch",
    ),
    (
        "SPEC-SE-PAIR",
        "SE pairs share one ADC (AIn with AIn+8)",
        "confirmed",
        "spec_sheet",
        "e.g. AI0&AI8, AI1&AI9 on the same converter",
    ),
    (
        "SPEC-BANK",
        "Same-ADC dual-SE uses banked scan at 500 kS/s/ch",
        "confirmed",
        "spec_sheet",
        "AI0:7 then AI8:15; gap via AIConv.Rate",
    ),
    (
        "SPEC-AICONV-RATE",
        "AIConv.Rate property controls inter-bank delay",
        "confirmed",
        "spec_sheet",
        "Software property name only; device register unknown",
    ),
    (
        "SPEC-TIMING-RES",
        "Timing resolution 10 ns, accuracy 50 ppm",
        "confirmed",
        "spec_sheet",
        "Sample clock timebase quality",
    ),
    (
        "SPEC-FIFO-AI",
        "Input FIFO 8191 samples shared among used channels",
        "confirmed",
        "spec_sheet",
        "Shared depth, not per-channel dedicated",
    ),
    (
        "SPEC-XFER-STREAM",
        "AI data path uses USB Signal Stream",
        "confirmed",
        "spec_sheet",
        "Also lists programmed I/O; stream is primary high-rate path",
    ),
    (
        "SPEC-PFI-TRIG",
        "PFI lines can source/sink AI timing and triggers",
        "confirmed",
        "spec_sheet",
        "PFI0:15 multifunctional with DIO",
    ),
    (
        "SPEC-SYNC-LAYER",
        "Multi-channel sync is hardware convert-on-shared-clock",
        "confirmed",
        "spec_derived",
        "Not host-side software alignment; follows from 16-ADC simultaneous model",
    ),
    (
        "SPEC-AO-4CH",
        "Four AO channels (out of sync-AI focus)",
        "confirmed",
        "spec_sheet",
        "Registered for system_map completeness; low priority for sync learning",
    ),
    (
        "SPEC-DIO-16",
        "Sixteen DIO/PFI lines",
        "confirmed",
        "spec_sheet",
        "Port0/line0:15",
    ),
    (
        "SPEC-FIFO-SHARED-DEPTH",
        "Effective per-channel FIFO depth shrinks with channel count",
        "confirmed",
        "spec_sheet",
        "8191-sample FIFO is a single shared pool; ~8191/n samples per channel when n channels are in the scan list",
    ),
    (
        "SPEC-DIFF-16",
        "Sixteen differential AI channels",
        "confirmed",
        "spec_sheet",
        "DIFF mode pairs AIn with AIn+8 terminals; 16 DIFF channels map 1:1 onto the 16 ADCs",
    ),
    (
        "SPEC-RANGE-LIST",
        "Multiple software-selectable AI input ranges",
        "confirmed",
        "spec_sheet",
        "Per-channel programmable input range up to +/-10 V full scale; exact range list per spec table, no per-range sync caveat stated",
    ),
    (
        "SPEC-MIN-RATE-NONE",
        "No documented hardware minimum AI sample rate",
        "confirmed",
        "spec_sheet",
        "Spec lists maximum rates only; low-rate operation bounded by timebase/divider, no minimum stated",
    ),
    (
        "SPEC-OEM-VARIANT",
        "USB-6453 OEM board-only variant exists",
        "confirmed",
        "spec_sheet",
        "OEM variant shares the same AI/sync spec; differences are enclosure/connector level, not converter topology",
    ),
]


def build_entries() -> list[dict[str, Any]]:
    out = []
    for ident, title, status, boundary, note in SPEC_ENTRIES:
        out.append(
            {
                "identifier": ident,
                "module": "spec_sync",
                "source_identifier": title,
                "status": status,
                "boundary": boundary,
                "note": note,
            }
        )
    return out


def entry_ids() -> list[str]:
    return [e[0] for e in SPEC_ENTRIES]
