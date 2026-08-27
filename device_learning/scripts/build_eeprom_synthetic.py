#!/usr/bin/env python3
"""Build synthetic FX2LP EEPROM reference image for pipeline testing only.

NOT a dump from the target device. Layout follows public FX2LP C2 boot format
offsets documented in manifests/eeprom_layout_ref.json.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
META = ROOT / "manifests" / "eeprom_synthetic_meta.json"

SIZE = 8192
BOOT = 0xC2
VID = 0x0000
PID = 0x0000
DID = 0x0000
CONFIG = 0x00


def build() -> bytes:
    data = bytearray([0xFF] * SIZE)
    data[0] = BOOT
    data[1:3] = VID.to_bytes(2, "little")
    data[3:5] = PID.to_bytes(2, "little")
    data[5:7] = DID.to_bytes(2, "little")
    data[7] = CONFIG
    # C2 data record: 16-byte payload to internal RAM 0x0000
    payload = bytes([0x02, 0x00, 0x10, 0x00]) + bytes((i & 0xFF) for i in range(12))
    data[8:10] = (len(payload)).to_bytes(2, "big")
    data[10:12] = (0x0000).to_bytes(2, "big")
    data[12 : 12 + len(payload)] = payload
    term = 12 + len(payload)
    data[term : term + 2] = (0x8001).to_bytes(2, "big")
    data[term + 2 : term + 4] = (0xE600).to_bytes(2, "big")
    data[term + 4] = 0x01
    return bytes(data)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blob = build()
    OUT.write_bytes(blob)
    meta = {
        "type": "synthetic_reference",
        "warning": "NOT a device dump — pipeline test fixture only",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "path": str(OUT.relative_to(ROOT)),
        "size_bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "boot_format": "C2",
        "boot_config_byte": f"0x{BOOT:02x}",
        "vid_hex": f"0x{VID:04x}",
        "pid_hex": f"0x{PID:04x}",
        "layout_ref": "manifests/eeprom_layout_ref.json",
    }
    META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
