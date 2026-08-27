#!/usr/bin/env python3
"""Parse a Xilinx Spartan-3 (.bit) configuration file into a structured summary.

The parser is intentionally defensive: every stage records its confidence and
falls back to ``candidate`` / ``unknown`` results instead of failing when a
field cannot be interpreted with certainty. The goal is a reproducible,
structured description of the bitstream, not a vendor tool replacement.

References (public documentation):
  * Xilinx UG332 "Spartan-3 Generation Configuration User Guide"
    - .bit container layout (key sections 'a'..'e')
    - Type-1 / Type-2 configuration packets and the 32-bit sync word
    - Configuration register map (CMD, FAR, FDRI, FLR, COR, IDCODE, ...)

Usage:
    python3 parse_bitstream.py [--bit PATH] [--out PATH]

Defaults resolve relative to the ``device_learning`` project root so the script
can be run from anywhere in the tree.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import struct
from datetime import datetime, timezone

# --- constants -------------------------------------------------------------

# 32-bit synchronization word that precedes the configuration command stream
# on Virtex / Spartan-3 generation devices.
SYNC_WORD = 0xAA995566

# .bit container key sections. Keys 'a'..'d' use a 16-bit big-endian length
# prefix and hold ASCII metadata; key 'e' uses a 32-bit length prefix and is
# followed by the raw configuration bitstream.
SHORT_KEYS = {
    0x61: "a_design_name",
    0x62: "b_part_name",
    0x63: "c_date",
    0x64: "d_time",
}
CONFIG_KEY = 0x65  # 'e'

# Configuration register addresses (Type-1 packet register field).
REGISTER_NAMES = {
    0x00: "CRC",
    0x01: "FAR",
    0x02: "FDRI",
    0x03: "FDRO",
    0x04: "CMD",
    0x05: "CTL",
    0x06: "MASK",
    0x07: "STAT",
    0x08: "LOUT",
    0x09: "COR",
    0x0A: "MFWR",
    0x0B: "FLR",
    0x0C: "KEY",
    0x0D: "CBC",
    0x0E: "IDCODE",
}

# CMD register command codes.
CMD_CODES = {
    0x00: "NULL",
    0x01: "WCFG",
    0x02: "MFWR",
    0x03: "DGHIGH/LFRM",
    0x04: "RCFG",
    0x05: "START",
    0x06: "RCAP",
    0x07: "RCRC",
    0x08: "AGHIGH",
    0x09: "SWITCH",
    0x0A: "GRESTORE",
    0x0B: "SHUTDOWN",
    0x0C: "GCAPTURE",
    0x0D: "DESYNCH",
}

# Known Spartan-3 device IDCODEs (public JTAG/IDCODE values), used only to
# annotate the parsed IDCODE with a family/device hint.
KNOWN_IDCODES = {
    0x0140D093: "family=spartan3 device=xc3s50",
    0x01414093: "family=spartan3 device=xc3s200",
    0x0141C093: "family=spartan3 device=xc3s400",
    0x01428093: "family=spartan3 device=xc3s1000",
    0x01434093: "family=spartan3 device=xc3s1500",
    0x01440093: "family=spartan3 device=xc3s2000",
    0x01448093: "family=spartan3 device=xc3s4000",
    0x01450093: "family=spartan3 device=xc3s5000",
}

# Packet opcodes.
OPCODES = {0: "NOP", 1: "READ", 2: "WRITE", 3: "RESERVED"}


def _mask_idcode(idcode: int) -> int:
    """IDCODE values carry a 4-bit revision field in the top nibble that varies
    between silicon steppings; mask it before matching against known devices."""
    return idcode & 0x0FFFFFFF


def redact_metadata(text: str) -> str:
    """Remove product-like tokens from container metadata strings.

    A product-like token is a run of >=2 letters immediately followed by >=1
    digit (e.g. an internal board/product code embedded in a design name).
    Such tokens are replaced with ``[redacted]`` so the structured output can be
    shared without leaking product identifiers. Generic tokens (plain words,
    dates, the ``UserID=`` label, file extensions) are preserved.
    """
    return re.sub(r"[A-Za-z]{2,}\d+[A-Za-z0-9]*", "[redacted]", text)


# --- container parsing -----------------------------------------------------

def parse_bit_container(data: bytes) -> dict:
    """Parse the .bit container header sections ('a'..'e').

    Returns a dict describing each section plus the offset/length of the raw
    configuration payload. Never raises on malformed input: unknown regions are
    reported with ``status`` flags instead.
    """
    result = {
        "magic_valid": False,
        "sections": {},
        "config_data_offset": None,
        "config_data_declared_length": None,
        "parse_notes": [],
    }

    pos = 0
    # The container opens with a short field-length record and a 0x0001 marker
    # before the keyed sections. We locate the first known key byte rather than
    # hard-coding the preamble length so minor header variants still parse.
    first_key = None
    for i in range(min(len(data), 64)):
        # Look for the 'a' (design name) key followed by a plausible 16-bit
        # length prefix, which marks the start of the keyed sections.
        if data[i] == 0x61 and i + 3 <= len(data):
            length = struct.unpack_from(">H", data, i + 1)[0]
            if 0 < length < 512 and i + 3 + length <= len(data):
                first_key = i
                break
    if first_key is None:
        result["parse_notes"].append("could not locate first keyed section")
        return result

    if first_key > 0:
        result["magic_valid"] = True
        result["preamble_hex"] = data[:first_key].hex()

    pos = first_key
    while pos < len(data):
        key = data[pos]
        if key in SHORT_KEYS:
            if pos + 3 > len(data):
                result["parse_notes"].append(
                    f"truncated short section at offset {pos}")
                break
            length = struct.unpack_from(">H", data, pos + 1)[0]
            raw = data[pos + 3: pos + 3 + length]
            value = raw.rstrip(b"\x00").decode("latin-1", errors="replace")
            name = SHORT_KEYS[key]
            entry = {
                "present": True,
                "offset": pos,
                "length": length,
            }
            if name == "a_design_name":
                entry["value_redacted"] = redact_metadata(value)
                entry["redaction_applied"] = entry["value_redacted"] != value
            else:
                entry["value"] = value
            result["sections"][name] = entry
            pos += 3 + length
        elif key == CONFIG_KEY:
            if pos + 5 > len(data):
                result["parse_notes"].append("truncated config section header")
                break
            length = struct.unpack_from(">I", data, pos + 1)[0]
            offset = pos + 5
            result["sections"]["e_config_data"] = {
                "present": True,
                "offset": offset,
                "length_bytes": length,
                "length_hex": f"0x{length:x}",
            }
            result["config_data_offset"] = offset
            result["config_data_declared_length"] = length
            break
        else:
            result["parse_notes"].append(
                f"unexpected key byte 0x{key:02x} at offset {pos}; stopping")
            break

    return result


# --- packet parsing --------------------------------------------------------

def decode_type1_header(word: int) -> dict:
    return {
        "type": 1,
        "opcode": OPCODES[(word >> 27) & 0x3],
        "register": (word >> 13) & 0x3FFF,
        "word_count": word & 0x7FF,
    }


def parse_packets(config: bytes, sync_offset: int) -> dict:
    """Walk the Type-1/Type-2 packet stream starting after the sync word.

    Large FDRI payloads are skipped (their location/size is recorded) so the
    walk continues to the trailing command packets (START/CRC/DESYNCH).
    """
    out = {
        "sync_word": f"0x{SYNC_WORD:08x}",
        "sync_offset_in_config": sync_offset,
        "packets": [],
        "registers": {},
        "cmd_sequence": [],
        "fdri": None,
        "parse_notes": [],
    }

    pos = sync_offset + 4  # skip the sync word itself
    n = len(config)
    last_register = None
    max_packets = 100000

    while pos + 4 <= n and len(out["packets"]) < max_packets:
        word = struct.unpack_from(">I", config, pos)[0]
        htype = (word >> 29) & 0x7
        start = pos
        pos += 4

        if htype == 1:
            hdr = decode_type1_header(word)
            reg = hdr["register"]
            reg_name = REGISTER_NAMES.get(reg, f"UNKNOWN_0x{reg:x}")
            wc = hdr["word_count"]
            payload = []
            if hdr["opcode"] == "WRITE" and wc > 0:
                for k in range(wc):
                    if pos + 4 > n:
                        break
                    payload.append(struct.unpack_from(">I", config, pos)[0])
                    pos += 4
            pkt = {
                "offset": start,
                "type": 1,
                "opcode": hdr["opcode"],
                "register": reg_name,
                "word_count": wc,
            }
            if payload:
                pkt["payload_hex"] = [f"0x{v:08x}" for v in payload]
            out["packets"].append(pkt)
            last_register = reg_name

            if hdr["opcode"] == "WRITE" and payload:
                _record_register_write(out, reg_name, payload)

        elif htype == 2:
            opcode = OPCODES[(word >> 27) & 0x3]
            wc = word & 0x07FFFFFF
            pkt = {
                "offset": start,
                "type": 2,
                "opcode": opcode,
                "follows_register": last_register,
                "word_count": wc,
            }
            out["packets"].append(pkt)
            # A Type-2 write following an FDRI Type-1 header carries the frame
            # data block. Record it and skip its payload.
            if last_register == "FDRI" and opcode == "WRITE":
                data_offset = pos
                data_bytes = wc * 4
                out["fdri"] = {
                    "word_count": wc,
                    "data_offset_in_config": data_offset,
                    "data_length_bytes": data_bytes,
                }
                pkt["is_frame_data"] = True
            pos += wc * 4
        else:
            # Not a recognized Type-1/Type-2 header. These occur as dummy/pad
            # words and as bare CRC words emitted right after an FDRI block.
            # Record them as filler and keep walking so the trailing command
            # packets (START / CRC / DESYNCH) are still captured.
            if word in (0xFFFFFFFF, 0x00000000, 0x20000000):
                out["packets"].append({
                    "offset": start, "type": "pad", "word": f"0x{word:08x}"})
            else:
                out.setdefault("trailing_words", []).append({
                    "offset": start, "word": f"0x{word:08x}",
                    "note": "filler / post-FDRI CRC candidate"})
            continue

    return out


def _record_register_write(out: dict, reg_name: str, payload: list) -> None:
    value = payload[0]
    if reg_name == "CMD":
        out["cmd_sequence"].append(CMD_CODES.get(value, f"0x{value:x}"))
    elif reg_name == "IDCODE":
        masked = _mask_idcode(value)
        out["registers"]["IDCODE"] = {
            "raw": f"0x{value:08x}",
            "device_hint": KNOWN_IDCODES.get(
                masked, KNOWN_IDCODES.get(value, "unknown")),
        }
    elif reg_name == "FLR":
        out["registers"]["FLR"] = {"value": value, "note": "frame length register"}
    elif reg_name == "COR":
        out["registers"]["COR"] = {"value": f"0x{value:08x}"}
    elif reg_name == "FAR":
        out["registers"].setdefault("FAR_writes", []).append(f"0x{value:08x}")
    elif reg_name == "CRC":
        out["registers"]["CRC"] = {"value": f"0x{value:08x}"}
    else:
        out["registers"].setdefault("other_writes", []).append(
            {"register": reg_name, "value": f"0x{value:08x}"})


# --- frame / IOB analysis --------------------------------------------------

def analyze_frames(config: bytes, fdri: dict, flr_value) -> dict:
    """Interpret the FDRI payload as a sequence of configuration frames.

    Frame length comes from the FLR register when available. Spartan-3 frame
    columns are laid out with the IOB (I/O) columns on the outer edges of the
    frame-address space, so we treat the outermost frame columns as the
    candidate location of IOB configuration words. All derived counts are
    reported with explicit confidence because exact per-column geometry for a
    specific device is not reconstructed here.
    """
    result = {
        "confidence": "candidate",
        "method": (
            "FDRI payload split into fixed-length frames using the FLR "
            "register; outer (edge) frame columns treated as candidate IOB "
            "configuration region per Spartan-3 column-based frame layout"
        ),
    }

    if not fdri:
        result["status"] = "unknown"
        result["note"] = "no FDRI frame-data block found"
        return result

    words = fdri["word_count"]
    result["fdri_word_count"] = words

    frame_len = None
    if isinstance(flr_value, int) and flr_value > 0:
        # FLR encodes frame length; the on-wire FDRI stream includes a trailing
        # pad frame, so report both the raw and the divisibility check.
        frame_len = flr_value
        result["frame_length_words"] = frame_len
        result["frame_length_source"] = "FLR register"
    else:
        result["frame_length_words"] = "unknown"
        result["frame_length_source"] = "unavailable"

    data_off = fdri["data_offset_in_config"]
    frame_words = list(struct.unpack_from(f">{words}I", config, data_off))

    nonzero = sum(1 for w in frame_words if w != 0)
    result["active_config_words"] = nonzero
    result["active_config_words_note"] = (
        "count of non-zero 32-bit words in the FDRI payload (upper bound on "
        "meaningfully-configured words)")

    if frame_len and frame_len > 0:
        full_frames = words // frame_len
        remainder = words % frame_len
        result["estimated_frame_count"] = full_frames
        result["trailing_words_after_last_full_frame"] = remainder
        if remainder:
            result["frame_alignment"] = (
                "candidate: FDRI word count not an exact multiple of FLR; "
                "remainder likely pad/CRC words")
        else:
            result["frame_alignment"] = "exact multiple of FLR"

        # Per-frame non-zero density.
        frames = [frame_words[i * frame_len:(i + 1) * frame_len]
                  for i in range(full_frames)]
        densities = [sum(1 for w in fr if w != 0) for fr in frames]

        # Outer (edge) columns as candidate IOB region. Without exact device
        # geometry we take a conservative window of the first and last frame
        # columns. This is explicitly a heuristic.
        edge = min(4, full_frames // 2) if full_frames else 0
        result["iob_edge_frame_window"] = edge
        if edge > 0:
            outer = densities[:edge] + densities[-edge:]
            iob_words = sum(outer)
        else:
            iob_words = 0
        result["candidate_iob_config_words"] = iob_words
        result["candidate_iob_confidence"] = "candidate/low"
        result["candidate_iob_note"] = (
            "non-zero words within the first/last frame columns; exact IOB "
            "frame mapping for this specific device is unknown")
        result["max_frame_density"] = max(densities) if densities else 0
        result["nonzero_frame_count"] = sum(1 for d in densities if d > 0)
    else:
        result["estimated_frame_count"] = "unknown"
        result["candidate_iob_config_words"] = "unknown"

    return result


# --- top level -------------------------------------------------------------

def parse_bitstream(bit_path: str) -> dict:
    with open(bit_path, "rb") as fh:
        data = fh.read()

    summary = {
        "schema_version": "1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": os.path.relpath(bit_path,
                                       os.path.dirname(os.path.dirname(bit_path))),
        "file_size_bytes": len(data),
        "parse_status": "partial",
        "family": "spartan3 (candidate, per part/IDCODE)",
    }

    container = parse_bit_container(data)
    summary["bit_container"] = container

    config_off = container.get("config_data_offset")
    declared_len = container.get("config_data_declared_length")

    config_info = {
        "declared_length_bytes": declared_len,
        "declared_length_hex": f"0x{declared_len:x}" if declared_len else None,
    }

    if config_off is not None:
        config = data[config_off:]
        sync_local = config.find(struct.pack(">I", SYNC_WORD))
        config_info["sync_found"] = sync_local >= 0
        config_info["sync_word"] = f"0x{SYNC_WORD:08x}"
        if sync_local >= 0:
            config_info["sync_offset_in_file"] = config_off + sync_local
            packets = parse_packets(config, sync_local)
            summary["config_data"] = config_info
            summary["packet_stream"] = {
                "sync_offset_in_config": packets["sync_offset_in_config"],
                "packet_count": len(packets["packets"]),
                "cmd_sequence": packets["cmd_sequence"],
                "registers": packets["registers"],
                "fdri": packets["fdri"],
                "parse_notes": packets["parse_notes"],
                "packets": packets["packets"],
            }

            flr_value = None
            flr = packets["registers"].get("FLR")
            if isinstance(flr, dict):
                flr_value = flr.get("value")

            summary["frame_analysis"] = analyze_frames(
                config, packets["fdri"], flr_value)
        else:
            summary["config_data"] = config_info
            summary["packet_stream"] = {"status": "unknown",
                                        "note": "sync word not found"}
    else:
        summary["config_data"] = config_info
        summary["packet_stream"] = {"status": "unknown",
                                    "note": "config payload not located"}

    # Overall status assessment.
    have_frames = isinstance(summary.get("frame_analysis"), dict) and \
        summary["frame_analysis"].get("fdri_word_count")
    if container.get("magic_valid") and config_off is not None and have_frames:
        summary["parse_status"] = "partial-ok"

    summary["unknowns"] = _collect_unknowns(summary)
    return summary


def _collect_unknowns(summary: dict) -> list:
    unknowns = []
    fa = summary.get("frame_analysis", {})
    if fa.get("frame_length_source") == "unavailable":
        unknowns.append("frame length (FLR) not found")
    if str(fa.get("candidate_iob_config_words")) == "unknown":
        unknowns.append("IOB configuration word count could not be estimated")
    if fa.get("frame_alignment", "").startswith("candidate"):
        unknowns.append(
            "FDRI word count not an exact multiple of frame length; frame "
            "count is a candidate estimate")
    unknowns.append(
        "exact per-column IOB frame mapping for the specific device is not "
        "reconstructed (candidate heuristic only)")
    return unknowns


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(here)
    default_bit = os.path.join(project_root, "firmware", "device.bit")
    default_out = os.path.join(project_root, "manifests", "frame_summary.json")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bit", default=default_bit, help="path to .bit file")
    ap.add_argument("--out", default=default_out,
                    help="path to output frame_summary.json")
    args = ap.parse_args()

    summary = parse_bitstream(args.bit)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    # Console echo of the key fields for quick inspection.
    print(f"wrote {args.out}")
    print(json.dumps({
        "parse_status": summary["parse_status"],
        "part_name": summary["bit_container"]["sections"]
            .get("b_part_name", {}).get("value"),
        "config_declared_length_hex":
            summary["config_data"].get("declared_length_hex"),
        "idcode": summary.get("packet_stream", {})
            .get("registers", {}).get("IDCODE"),
        "cmd_sequence": summary.get("packet_stream", {}).get("cmd_sequence"),
        "frame_analysis": {
            k: summary.get("frame_analysis", {}).get(k)
            for k in ("frame_length_words", "fdri_word_count",
                      "estimated_frame_count", "active_config_words",
                      "candidate_iob_config_words", "confidence")
        },
    }, indent=2))


if __name__ == "__main__":
    main()
