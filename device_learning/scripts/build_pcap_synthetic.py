#!/usr/bin/env python3
"""Build minimal synthetic pcapng fixture for pipeline tests (NOT device capture)."""
from __future__ import annotations

import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b" / "fixtures" / "usb_enum_synthetic_reference.pcapng"
META = ROOT / "manifests" / "pcap_synthetic_meta.json"


def build_minimal_pcapng() -> bytes:
    """Smallest valid pcapng section header block (Wireshark-readable shell)."""
    body = struct.pack("<IHHq", 0x1A2B3C4D, 1, 0, -1)
    total = 12 + len(body) + 4
    return struct.pack("<II", 0x0A0D0D0A, total) + body + struct.pack("<I", total)


def main() -> None:
    data = build_minimal_pcapng()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    meta = {
        "type": "synthetic_reference",
        "warning": "NOT a device USB capture — pipeline test fixture only",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path": str(OUT.relative_to(ROOT)),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic": "pcapng",
    }
    META.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
