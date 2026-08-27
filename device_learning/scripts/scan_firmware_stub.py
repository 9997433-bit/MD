#!/usr/bin/env python3
"""Stub 8051 firmware scan when EEPROM dump is available."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EEPROM = ROOT / "phase_b" / "captures" / "eeprom.bin"
FW_OFFSET = 0x10


def scan_firmware(fw: bytes) -> dict:
    if len(fw) < 16:
        return {"status": "too_short", "size": len(fw)}
    # Heuristic: look for 8051 LJMP at reset vector area
    header = fw[:32].hex()
    return {
        "status": "observed",
        "size_bytes": len(fw),
        "header_hex": header,
        "boundary": "Not disassembled; use Ghidra 8051 or mcs51-disasm",
        "next_steps": [
            "Load firmware slice at offset 0x10 into Ghidra with 8051 processor",
            "Map XRAM/codec per CY7C68013A memory map",
            "Cross-reference USB descriptor tables",
        ],
    }


def main() -> None:
    if not EEPROM.exists():
        meta = {"status": "missing", "path": str(EEPROM.relative_to(ROOT))}
    else:
        data = EEPROM.read_bytes()
        fw = data[FW_OFFSET:] if len(data) > FW_OFFSET else b""
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "eeprom_size": len(data),
            "firmware_offset": FW_OFFSET,
            "firmware_scan": scan_firmware(fw),
        }
    out = ROOT / "manifests" / "firmware_scan.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
