#!/usr/bin/env python3
"""Build synthetic FX2LP EEPROM reference image for pipeline testing only.

NOT a dump from the target device. Used to verify analyze_eeprom.py and
scan_firmware_stub.py without hardware.
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
BOOT = 0xC0  # valid firmware, no descriptor override
VID = 0x0000  # intentionally zero — do not infer device identity
PID = 0x0000
FW_OFFSET = 0x10


def build() -> bytes:
    data = bytearray([0xFF] * SIZE)
    data[0] = BOOT
    data[8:10] = VID.to_bytes(2, "little")
    data[10:12] = PID.to_bytes(2, "little")
    data[12:14] = (0x0001).to_bytes(2, "little")  # device release
    data[14] = 0x80  # config: bus-powered
    # Minimal 8051-like header pattern (not real firmware)
    data[FW_OFFSET : FW_OFFSET + 4] = bytes([0x02, 0x00, 0x10, 0x00])  # LJMP-ish placeholder
    for i in range(FW_OFFSET + 4, min(FW_OFFSET + 256, SIZE)):
        data[i] = i & 0xFF
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
        "boot_config_byte": f"0x{BOOT:02x}",
        "vid_hex": f"0x{VID:04x}",
        "pid_hex": f"0x{PID:04x}",
        "firmware_offset": FW_OFFSET,
    }
    META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
