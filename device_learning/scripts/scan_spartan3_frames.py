#!/usr/bin/env python3
"""Deep scan of Spartan-3 configuration frames."""
from __future__ import annotations

import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from parse_bit_header import parse_bit


def classify_word(w: int) -> str:
    top3 = (w >> 13) & 0x7
    if top3 == 1:
        return "type1"
    if top3 == 2:
        return "type2"
    if w == 0:
        return "zero"
    return "other"


def scan_config(config: bytes) -> dict:
    words = [struct.unpack(">H", config[i : i + 2])[0] for i in range(0, len(config) - 1, 2)]
    classes = Counter(classify_word(w) for w in words)
    return {
        "word_count": len(words),
        "class_counts": dict(classes),
        "zero_word_ratio": round(classes.get("zero", 0) / max(len(words), 1), 4),
    }


def main() -> None:
    bit_path = ROOT / "firmware" / "device.bit"
    data = bit_path.read_bytes()
    meta = parse_bit(data)
    offset = meta["bitstream_data_offset"]
    length = meta["bitstream_length"]
    config = data[offset : offset + length]
    result = {
        "device": meta.get("part_name"),
        "config_length": length,
        "scan": scan_config(config),
        "notes": "Heuristic Spartan-3 frame classifier.",
    }
    out = ROOT / "manifests" / "frame_deep.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
