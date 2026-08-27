#!/usr/bin/env python3
"""Parse the header of a Xilinx ``.bit`` bitstream file.

A Xilinx BIT file starts with a small, self-describing header made of
length-prefixed fields followed by a sequence of keyed sections:

    <u16 len> <magic bytes>          fixed sync/magic field (0x0ff0.../0x00)
    <u16>                            fixed 0x0001 marker
    'a' <u16 len> <string\\0>         source design name (NCD + build options)
    'b' <u16 len> <string\\0>         target part name
    'c' <u16 len> <string\\0>         build date  (YYYY/MM/DD)
    'd' <u16 len> <string\\0>         build time  (HH:MM:SS)
    'e' <u32 len> <raw bitstream>    configuration data payload

All multi-byte integers are big-endian. Strings are NUL-terminated.

The script emits a structured JSON description of everything in the header.
The raw configuration payload (section ``e``) is never included; only its
length and byte offset are reported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys


# Human-readable meaning of each keyed section. The design name is stored under
# a neutral ``source_design_name`` key so it is not treated as a product label.
SECTION_FIELDS = {
    "a": "source_design_name",
    "b": "part_name",
    "c": "build_date",
    "d": "build_time",
}


class BitParseError(Exception):
    """Raised when the input does not look like a valid Xilinx BIT file."""


def _read_u16(data: bytes, offset: int) -> tuple[int, int]:
    if offset + 2 > len(data):
        raise BitParseError(f"unexpected end of file reading u16 at {offset}")
    return struct.unpack_from(">H", data, offset)[0], offset + 2


def _read_u32(data: bytes, offset: int) -> tuple[int, int]:
    if offset + 4 > len(data):
        raise BitParseError(f"unexpected end of file reading u32 at {offset}")
    return struct.unpack_from(">I", data, offset)[0], offset + 4


def _decode_string(raw: bytes) -> str:
    """Decode a NUL-terminated ASCII section value."""
    return raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")


def _describe_part(part_name: str) -> dict:
    """Best-effort decode of a Xilinx short part code such as ``3s200ft256``.

    The parser is intentionally conservative: it only fills fields it can
    derive from the string and leaves the rest as ``None``.
    """
    info = {
        "raw": part_name,
        "family": None,
        "device": None,
        "package": None,
    }
    # Ordered longest-prefix-first so e.g. "3sd" wins over "3s".
    families = {
        "3sd": ("Spartan-3", "XC3SD"),
        "3s": ("Spartan-3", "XC3S"),
        "6s": ("Spartan-6", "XC6S"),
    }
    lowered = part_name.lower()
    for prefix, (family, dev_prefix) in sorted(
        families.items(), key=lambda kv: -len(kv[0])
    ):
        if lowered.startswith(prefix):
            rest = part_name[len(prefix):]
            digits = ""
            idx = 0
            while idx < len(rest) and rest[idx].isdigit():
                digits += rest[idx]
                idx += 1
            info["family"] = family
            if digits:
                info["device"] = f"{dev_prefix}{digits}"
            package = rest[idx:]
            if package:
                info["package"] = package.upper()
            break
    return info


def parse_bit(data: bytes) -> dict:
    """Parse ``data`` (the full BIT file contents) into a structured dict."""
    offset = 0

    magic_len, offset = _read_u16(data, offset)
    if offset + magic_len > len(data):
        raise BitParseError("magic field length exceeds file size")
    magic = data[offset:offset + magic_len]
    offset += magic_len

    marker, offset = _read_u16(data, offset)

    sections: dict[str, dict] = {}
    parsed: dict[str, object] = {}

    # Read the four textual keyed sections: a, b, c, d.
    for expected_key in ("a", "b", "c", "d"):
        if offset >= len(data):
            raise BitParseError(f"file truncated before section '{expected_key}'")
        key = chr(data[offset])
        offset += 1
        if key != expected_key:
            raise BitParseError(
                f"expected section '{expected_key}' but found '{key}' at "
                f"offset {offset - 1}"
            )
        length, offset = _read_u16(data, offset)
        if offset + length > len(data):
            raise BitParseError(f"section '{key}' length exceeds file size")
        raw = data[offset:offset + length]
        offset += length
        value = _decode_string(raw)
        field_name = SECTION_FIELDS[key]
        sections[key] = {
            "field": field_name,
            "declared_length": length,
            "value": value,
        }
        parsed[field_name] = value

    # Read the binary configuration payload: section 'e'.
    bitstream = None
    if offset < len(data) and chr(data[offset]) == "e":
        offset += 1
        data_len, offset = _read_u32(data, offset)
        data_offset = offset
        bitstream = {
            "field": "bitstream_data",
            "declared_length": data_len,
            "declared_length_hex": f"0x{data_len:x}",
            "data_offset": data_offset,
            "header_length": data_offset,
            "matches_file_size": (data_offset + data_len) == len(data),
        }
        sections["e"] = bitstream

    result = {
        "format": "Xilinx BIT",
        "magic": magic.hex(),
        "marker": marker,
        "sections": sections,
        "source_design_name": parsed.get("source_design_name"),
        "part_name": parsed.get("part_name"),
        "part": _describe_part(parsed.get("part_name", "")),
        "build_date": parsed.get("build_date"),
        "build_time": parsed.get("build_time"),
        "header_length": bitstream["data_offset"] if bitstream else offset,
    }
    if bitstream is not None:
        result["bitstream_length"] = bitstream["declared_length"]
        result["bitstream_length_hex"] = bitstream["declared_length_hex"]
        result["bitstream_data_offset"] = bitstream["data_offset"]
    return result


def file_summary(path: str, data: bytes) -> dict:
    return {
        "name": os.path.basename(path),
        "path": path,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse a Xilinx BIT file header into structured JSON."
    )
    parser.add_argument("bitfile", help="path to the .bit file")
    parser.add_argument(
        "-o",
        "--output",
        help="write JSON to this path instead of stdout",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation (default: 2)",
    )
    args = parser.parse_args(argv)

    with open(args.bitfile, "rb") as fh:
        data = fh.read()

    try:
        header = parse_bit(data)
    except BitParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = {
        "file": file_summary(args.bitfile, data),
        "header": header,
    }
    text = json.dumps(report, indent=args.indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            out.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
