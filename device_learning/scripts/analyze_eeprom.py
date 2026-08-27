#!/usr/bin/env python3
"""Analyze EEPROM dump if present."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EEPROM = ROOT / "phase_b" / "captures" / "eeprom.bin"
LAYOUT = ROOT / "manifests" / "eeprom_layout_ref.json"


def main() -> None:
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    if not EEPROM.exists():
        meta = {
            "status": "missing",
            "path": str(EEPROM.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "layout_ref": "manifests/eeprom_layout_ref.json",
            "note": "Place eeprom.bin in phase_b/captures/ and re-run",
        }
    else:
        data = EEPROM.read_bytes()
        boot = data[0] if data else None
        vid = int.from_bytes(data[8:10], "little") if len(data) >= 10 else None
        pid = int.from_bytes(data[10:12], "little") if len(data) >= 12 else None
        meta = {
            "status": "observed",
            "path": str(EEPROM.relative_to(ROOT)),
            "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "boot_config_byte": f"0x{boot:02x}" if boot is not None else None,
            "vid_hex": f"0x{vid:04x}" if vid is not None else None,
            "pid_hex": f"0x{pid:04x}" if pid is not None else None,
            "firmware_offset": 0x10,
            "firmware_size_bytes": max(0, len(data) - 0x10),
            "layout_ref": "manifests/eeprom_layout_ref.json",
            "boundary": "VID/PID observed only; firmware not disassembled",
        }
    out = ROOT / "manifests" / "eeprom_meta.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
