#!/usr/bin/env python3
"""Deep Spartan-3 configuration-frame scanner.

This is a *statistics-focused* companion to ``parse_bitstream.py``. Where the
sibling script produces a structural summary, this script drills into three
specific dimensions of the configuration bitstream and reports them with
explicit confidence:

  1. Frame Address Register (FAR) address distribution.
  2. Type-1 / Type-2 packet (frame) type counts.
  3. Configuration register write inventory.

Everything is derived from the ``.bit`` configuration segment only. No vendor
netlist, device geometry beyond the public documentation, or run-time behaviour
is assumed; derived quantities carry a ``confidence`` field and fall back to
``candidate`` / ``unknown`` rather than guessing.

References (public documentation):
  * Xilinx UG332 "Spartan-3 Generation Configuration User Guide"
  * Xilinx XAPP452 "Spartan-3 FPGA Family Advanced Configuration Architecture"
    - Figure 2: Frame Address Register bit layout
        [31:29] reserved, [28:25] Column (Block) Address, [24:19] Major Address,
        [18:10] Minor Address, [9:0] FRM_BYTE (unused)
    - Table 12/13: column types, frames-per-column, and column-address codes

Usage:
    python3 scan_spartan3_frames.py [--bit PATH] [--out PATH]

Defaults resolve relative to the ``device_learning`` project root so the script
can be run from anywhere in the tree.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from collections import Counter
from datetime import datetime, timezone

# Reuse the vetted container / packet walker from the sibling parser so the two
# scripts cannot drift apart on how the .bit segment is located and decoded.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_bitstream import (  # noqa: E402
    SYNC_WORD,
    parse_bit_container,
    parse_packets,
)

# --- Frame Address Register field layout (XAPP452 Figure 2) ----------------
# Bit windows within the 32-bit FAR value.
FAR_RESERVED_SHIFT, FAR_RESERVED_MASK = 29, 0x7        # [31:29]
FAR_COLUMN_SHIFT, FAR_COLUMN_MASK = 25, 0xF            # [28:25]
FAR_MAJOR_SHIFT, FAR_MAJOR_MASK = 19, 0x3F             # [24:19]
FAR_MINOR_SHIFT, FAR_MINOR_MASK = 10, 0x1FF            # [18:10]
FAR_FRMBYTE_MASK = 0x3FF                               # [9:0]

# Column (Block) Address codes. Only the low two bits are used in practice; all
# CLB / IOB / TERM / IOI / GCLK frames share code 0 (XAPP452 Table 13).
COLUMN_ADDRESS_TYPES = {
    0b00: "CLB/IOB/IOI/TERM/GCLK (logic & I/O block)",
    0b01: "Block RAM content",
    0b10: "Block RAM interconnect",
    0b11: "reserved/unknown",
}

# Documented frames-per-column by column type (XAPP452 Table 12). Used only to
# form a candidate estimate of how many logic-block columns the frame stream
# spans; the exact per-device column inventory for this specific part is not
# encoded in the bitstream and is therefore not reconstructed.
FRAMES_PER_COLUMN = {
    "TERM": 2,
    "IOI": 19,
    "CLB": 19,
    "GCLK": 3,
    "BRAM_content": 76,
    "BRAM_interconnect": 19,
}
# The dominant logic-block column length (CLB / IOI) used for the candidate
# column-count estimate.
CLB_LIKE_FRAMES_PER_COLUMN = 19

# Header-class codes for the 16-bit word classifier (top three bits of each
# 16-bit word, matching the Type-1 / Type-2 packet opcode field position).
WORD_CLASS_TYPE1 = 0b001
WORD_CLASS_TYPE2 = 0b010


def decode_far(value: int) -> dict:
    """Decode a raw 32-bit FAR value into its documented sub-fields."""
    column = (value >> FAR_COLUMN_SHIFT) & FAR_COLUMN_MASK
    return {
        "raw": f"0x{value:08x}",
        "reserved": (value >> FAR_RESERVED_SHIFT) & FAR_RESERVED_MASK,
        "column_address": column,
        "column_address_type": COLUMN_ADDRESS_TYPES.get(
            column & 0x3, "reserved/unknown"),
        "major_address": (value >> FAR_MAJOR_SHIFT) & FAR_MAJOR_MASK,
        "minor_address": (value >> FAR_MINOR_SHIFT) & FAR_MINOR_MASK,
        "frm_byte": value & FAR_FRMBYTE_MASK,
    }


# --- statistics collectors -------------------------------------------------

def far_distribution(packets: dict) -> dict:
    """Summarise the FAR address writes and the resulting address coverage.

    Spartan-3 loads frame data with a single FAR write followed by a large FDRI
    burst; internal counters then auto-increment the minor, major, and block
    address for every subsequent frame (XAPP452, "Configuration Frame
    Addressing"). The per-frame addresses are therefore *not* explicitly
    present in the bitstream, so the block-type distribution below is reported
    against the explicit writes only, with the auto-increment behaviour noted.
    """
    raw_writes = packets["registers"].get("FAR_writes", [])
    decoded = [decode_far(int(v, 16)) for v in raw_writes]

    column_hist = Counter(d["column_address_type"] for d in decoded)
    major_values = sorted({d["major_address"] for d in decoded})
    minor_values = sorted({d["minor_address"] for d in decoded})

    return {
        "confidence": "confirmed (explicit writes) / candidate (per-frame)",
        "explicit_far_write_count": len(decoded),
        "unique_far_values": len(set(raw_writes)),
        "explicit_far_writes": decoded,
        "column_address_histogram": dict(column_hist),
        "distinct_major_addresses": major_values,
        "distinct_minor_addresses": minor_values,
        "auto_increment_note": (
            "only the explicit FAR write(s) above are encoded; all remaining "
            "frame addresses are produced by the device's internal "
            "minor->major->block auto-increment during the FDRI burst and are "
            "not present in the bitstream (per XAPP452)"),
    }


def frame_type_counts(packets: dict, frame_analysis: dict) -> dict:
    """Count packet (frame) types and derive candidate frame-level totals."""
    pkts = packets["packets"]
    type_counter = Counter()
    opcode_counter = Counter()
    for p in pkts:
        t = p.get("type")
        type_counter[f"type_{t}" if t in (1, 2) else str(t)] += 1
        op = p.get("opcode")
        if op:
            opcode_counter[op] += 1

    out = {
        "confidence": "confirmed (packets) / candidate (frame estimates)",
        "packet_type_counts": dict(type_counter),
        "opcode_counts": dict(opcode_counter),
        "total_packets": len(pkts),
        "trailing_filler_words": len(packets.get("trailing_words", [])),
    }

    # Frame-level (FDRI) estimates come from the sibling structural analysis.
    fdri = packets.get("fdri")
    if fdri:
        out["fdri_frame_data_word_count"] = fdri["word_count"]
    for key in ("frame_length_words", "estimated_frame_count",
                "trailing_words_after_last_full_frame", "frame_alignment",
                "nonzero_frame_count", "active_config_words"):
        if key in frame_analysis:
            out[key] = frame_analysis[key]

    # Candidate estimate of the number of logic-block columns spanned, using the
    # documented CLB/IOI frame-per-column length. Explicitly a heuristic.
    fc = frame_analysis.get("estimated_frame_count")
    if isinstance(fc, int) and fc > 0:
        out["implied_logic_column_count_candidate"] = round(
            fc / CLB_LIKE_FRAMES_PER_COLUMN)
        out["implied_logic_column_count_note"] = (
            f"estimated_frame_count / {CLB_LIKE_FRAMES_PER_COLUMN} "
            "(CLB/IOI frames-per-column); candidate only, exact per-device "
            "column inventory is not encoded in the bitstream")
    # The final data frame is always a pad frame (UG332/XAPP452).
    out["pad_frame_present"] = "candidate: last configuration frame is a pad frame per spec"
    return out


def word_class_scan(config_segment: bytes) -> dict:
    """Coarse 16-bit word histogram over the raw configuration segment.

    Each 16-bit word is bucketed by the top three bits, which line up with the
    packet opcode field: class ``001`` and ``010`` mirror the Type-1 / Type-2
    header signatures, ``zero`` counts all-zero words (padding), and ``other``
    covers the remaining data/CRC words. This is an intentionally simple,
    reproducible density measure over the whole segment, complementary to the
    packet-accurate counts in ``frame_type_counts``.
    """
    n = len(config_segment) // 2
    words = struct.unpack_from(f">{n}H", config_segment, 0)
    counts = {"zero": 0, "type1": 0, "type2": 0, "other": 0}
    for w in words:
        if w == 0:
            counts["zero"] += 1
        elif (w >> 13) == WORD_CLASS_TYPE1:
            counts["type1"] += 1
        elif (w >> 13) == WORD_CLASS_TYPE2:
            counts["type2"] += 1
        else:
            counts["other"] += 1
    return {
        "confidence": "candidate (heuristic 16-bit classifier)",
        "word_count": n,
        "class_counts": counts,
        "zero_word_ratio": round(counts["zero"] / n, 4) if n else 0.0,
    }


def register_write_inventory(packets: dict) -> dict:
    """Inventory every Type-1 register write with its payload."""
    writes = []
    reg_counter = Counter()
    for p in packets["packets"]:
        if p.get("type") == 1 and p.get("opcode") == "WRITE" and p.get("payload_hex"):
            reg = p["register"]
            reg_counter[reg] += 1
            writes.append({
                "offset": p["offset"],
                "register": reg,
                "word_count": p["word_count"],
                "payload_hex": p["payload_hex"],
            })
    return {
        "confidence": "confirmed",
        "register_write_counts": dict(reg_counter),
        "distinct_registers_written": sorted(reg_counter),
        "cmd_sequence": packets["cmd_sequence"],
        "decoded_registers": packets["registers"],
        "writes": writes,
    }


# --- top level -------------------------------------------------------------

def scan(bit_path: str) -> dict:
    with open(bit_path, "rb") as fh:
        data = fh.read()

    result = {
        "schema_version": "1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": os.path.relpath(
            bit_path, os.path.dirname(os.path.dirname(bit_path))),
        "file_size_bytes": len(data),
        "reference": "UG332 / XAPP452 (public Xilinx documentation)",
        "scan_status": "partial",
    }

    container = parse_bit_container(data)
    config_off = container.get("config_data_offset")
    if config_off is None:
        result["scan_status"] = "unknown"
        result["note"] = "configuration segment not located"
        return result

    declared_len = container.get("config_data_declared_length")
    part_name = (container.get("sections", {})
                 .get("b_part_name", {}).get("value"))

    config = data[config_off:]
    sync_local = config.find(struct.pack(">I", SYNC_WORD))
    if sync_local < 0:
        result["scan_status"] = "unknown"
        result["note"] = "sync word not found in configuration segment"
        return result

    packets = parse_packets(config, sync_local)

    # Coarse whole-segment word histogram over the declared configuration bytes.
    seg_end = config_off + declared_len if declared_len else len(data)
    result["device"] = part_name
    result["config_length"] = declared_len
    result["scan"] = word_class_scan(data[config_off:seg_end])
    result["notes"] = (
        "Heuristic Spartan-3 frame classifier (16-bit word top-3-bit header "
        "class); see far_address_distribution / frame_type_counts / "
        "register_write_inventory for packet-accurate detail.")

    # Recover the FLR-based frame view the same way the sibling parser does so
    # frame-count estimates stay consistent across manifests.
    from parse_bitstream import analyze_frames
    flr = packets["registers"].get("FLR")
    flr_value = flr.get("value") if isinstance(flr, dict) else None
    frame_analysis = analyze_frames(config, packets["fdri"], flr_value)

    result["config_segment"] = {
        "offset_in_file": config_off,
        "declared_length_bytes": container.get("config_data_declared_length"),
        "sync_offset_in_file": config_off + sync_local,
        "sync_word": f"0x{SYNC_WORD:08x}",
    }
    result["far_address_distribution"] = far_distribution(packets)
    result["frame_type_counts"] = frame_type_counts(packets, frame_analysis)
    result["register_write_inventory"] = register_write_inventory(packets)
    result["scan_status"] = "partial-ok"
    result["unknowns"] = [
        "per-frame FAR addresses are auto-incremented internally and not "
        "encoded in the bitstream (candidate reconstruction only)",
        "exact per-device column inventory (major-address range) is not "
        "reconstructed; column-count estimate is a candidate heuristic",
    ]
    return result


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(here)
    default_bit = os.path.join(project_root, "firmware", "device.bit")
    default_out = os.path.join(project_root, "manifests", "frame_deep.json")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bit", default=default_bit, help="path to .bit file")
    ap.add_argument("--out", default=default_out,
                    help="path to output frame_deep.json")
    args = ap.parse_args()

    result = scan(args.bit)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")

    print(f"wrote {args.out}")
    print(json.dumps({
        "scan_status": result["scan_status"],
        "far": {
            k: result.get("far_address_distribution", {}).get(k)
            for k in ("explicit_far_write_count", "unique_far_values",
                      "column_address_histogram")
        },
        "frames": {
            k: result.get("frame_type_counts", {}).get(k)
            for k in ("packet_type_counts", "estimated_frame_count",
                      "implied_logic_column_count_candidate")
        },
        "registers": result.get("register_write_inventory", {})
            .get("register_write_counts"),
    }, indent=2))


if __name__ == "__main__":
    main()
