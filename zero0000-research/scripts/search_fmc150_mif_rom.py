#!/usr/bin/env python3
"""
Search for contiguous SPI configuration table blobs as used by samprager/KC705_DDS
(blk_mem_gen INIT from .mif / .coe).

Unlike search_spi_constants.py (scattered LE16/32 word hits), this looks for the
full sequence of register words as contiguous little/big-endian bytes — the
signature of a BRAM/ROM init of an MIF table.

Source tables (verified 2026-08-28 against upstream):
  https://github.com/samprager/KC705_DDS
  .../Vivado.runs/ads62p49_init_mem_synth_1/ads62p49_init_mem.mif
  .../Vivado.runs/dac3283_init_mem_synth_1/dac3283_init_mem.mif
  .../Vivado.runs/cdce72010_init_mem_int_synth_1/cdce72010_init_mem_int.mif
  .../Vivado.runs/cdce72010_init_mem_ext_synth_1/cdce72010_init_mem_ext.mif
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

# ads62p49_init_mem.mif — 16-bit words; 0x4180 = CLKOUT DDR LVDS
ADS62P49_MIF = [
    0x0080,
    0x2000,
    0x3F20,
    0x4008,
    0x4180,
    0x4400,
    0x5044,
    0x5200,
    0x5340,
    0x55C0,
    0x5700,
    0x6200,
    0x6300,
    0x6640,
    0x68C0,
    0x6A00,
    0x7500,
    0x7600,
]

# dac3283_init_mem.mif — 16-bit; 0x0121 = CONFIG1 (~2x interp)
DAC3283_MIF = [
    0x0070,
    0x0121,
    0x0200,
    0x0310,
    0x04FF,
    0x0500,
    0x0600,
    0x0700,
    0x0800,
    0x0955,
    0x0AAA,
    0x0B55,
    0x0CAA,
    0x0D55,
    0x0EAA,
    0x0F55,
    0x10AA,
    0x1124,
    0x1202,
    0x13C2,
    0x1400,
    0x1500,
    0x1600,
    0x1704,
    0x1883,
    0x1900,
    0x1A00,
    0x1B00,
    0x1C00,
    0x1D00,
    0x1E24,
    0x1F52,
]

# cdce72010_init_mem_int.mif — 32-bit SPI words (data28<<4)|addr
CDCE_INT_MIF = [
    0x683C0350,
    0x68000021,
    0x83800002,
    0x68000003,
    0xE9800004,
    0x68000005,
    0x68000006,
    0x83400017,
    0x68000098,
    0x68050CC9,
    0x05FC270A,
    0x0000040B,
    0x0000180C,
]

# cdce72010_init_mem_ext.mif
CDCE_EXT_MIF = [
    0x683C0310,
    0x68000021,
    0x83800002,
    0x68000003,
    0xE9800004,
    0x68000005,
    0x68000006,
    0x83400017,
    0x68000098,
    0x68050CC9,
    0x05FC270A,
    0x2800440B,
    0x0000180C,
]


def words_to_bytes(words: list[int], width: int, endian: str) -> bytes:
    if endian not in ("<", ">"):
        raise ValueError(endian)
    if width == 16:
        fmt = endian + "H"
        return b"".join(struct.pack(fmt, w & 0xFFFF) for w in words)
    if width == 32:
        fmt = endian + "I"
        return b"".join(struct.pack(fmt, w & 0xFFFFFFFF) for w in words)
    raise ValueError(width)


def find_all(hay: bytes, needle: bytes) -> list[int]:
    if not needle:
        return []
    out: list[int] = []
    start = 0
    while True:
        i = hay.find(needle, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out


def longest_prefix_hit(
    hay: bytes, words: list[int], width: int, endian: str
) -> tuple[int, int]:
    """Return (n_words_matched, first_offset) for longest leading contiguous prefix."""
    for n in range(len(words), 1, -1):
        blob = words_to_bytes(words[:n], width, endian)
        hits = find_all(hay, blob)
        if hits:
            return n, hits[0]
    return 0, -1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bin_path", type=Path)
    args = ap.parse_args()
    data = args.bin_path.read_bytes()
    print(f"file={args.bin_path} size={len(data)}")
    print("tables=KC705_DDS Vivado.runs *.mif (ads/dac/cdce int+ext)")

    cases = [
        ("ADS62P49_MIF", ADS62P49_MIF, 16),
        ("DAC3283_MIF", DAC3283_MIF, 16),
        ("CDCE_INT_MIF", CDCE_INT_MIF, 32),
        ("CDCE_EXT_MIF", CDCE_EXT_MIF, 32),
    ]
    for name, words, width in cases:
        for endian, tag in (("<", "LE"), (">", "BE")):
            label = f"{name}_{tag}{width}"
            full = words_to_bytes(words, width, endian)
            full_hits = find_all(data, full)
            n, off = longest_prefix_hit(data, words, width, endian)
            print(f"\n=== {label} ===")
            print(
                f"full_table_bytes={len(full)} full_hits={len(full_hits)} "
                f"first={full_hits[0] if full_hits else None}"
            )
            print(f"longest_prefix_words={n}/{len(words)} offset={off}")
            if n >= 4:
                print("  NOTE: long contiguous prefix — inspect BRAM region")
            elif n <= 2:
                print("  OK: no meaningful contiguous MIF-style ROM blob")


if __name__ == "__main__":
    main()
