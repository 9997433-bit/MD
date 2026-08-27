#!/usr/bin/env python3
"""Compute entropy statistics for the Xilinx configuration data segment."""
from __future__ import annotations

import json
import math
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIT = ROOT / "firmware" / "device.bit"
SYNC = 0xAA995566


def find_config_segment(data: bytes) -> bytes:
    idx = data.find(struct.pack(">I", SYNC))
    if idx < 0:
        return b""
    return data[idx:]


def shannon_entropy(blob: bytes) -> float:
    if not blob:
        return 0.0
    counts = Counter(blob)
    n = len(blob)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def main() -> None:
    if not BIT.exists():
        meta = {"status": "missing"}
    else:
        raw = BIT.read_bytes()
        cfg = find_config_segment(raw)
        byte_entropy = shannon_entropy(cfg)
        zero_ratio = cfg.count(0) / len(cfg) if cfg else 0.0
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(BIT.relative_to(ROOT)),
            "config_segment_bytes": len(cfg),
            "byte_entropy_bits": round(byte_entropy, 4),
            "zero_byte_ratio": round(zero_ratio, 4),
            "interpretation": "candidate",
            "boundary": "High entropy expected in encrypted/compressed config; zero ratio relates to FRM-010 padding",
            "supports_identifiers": ["FRM-010-PADDING", "FRM-023-ZERO-RATIO"],
        }

    out = ROOT / "manifests" / "config_entropy.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"byte_entropy_bits": meta.get("byte_entropy_bits")}, indent=2))


if __name__ == "__main__":
    main()
