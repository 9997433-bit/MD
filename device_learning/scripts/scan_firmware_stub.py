#!/usr/bin/env python3
"""Scan firmware from real EEPROM or synthetic fixture."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "phase_b" / "captures" / "eeprom.bin"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
FW_OFFSET = 0x10


def scan_firmware(fw: bytes, source: str) -> dict:
    if len(fw) < 16:
        return {"status": "too_short", "size": len(fw), "source": source}
    return {
        "status": "observed" if source == "device_capture" else "synthetic_pipeline_test",
        "source": source,
        "size_bytes": len(fw),
        "header_hex": fw[:32].hex(),
        "boundary": "Not disassembled; use Ghidra 8051 when real dump available",
    }


def main() -> None:
    if REAL.exists():
        data = REAL.read_bytes()
        source = "device_capture"
    elif SYNTH.exists():
        data = SYNTH.read_bytes()
        source = "synthetic_reference"
    else:
        meta = {"status": "missing", "path": str(REAL.relative_to(ROOT))}
        (ROOT / "manifests" / "firmware_scan.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(json.dumps(meta, indent=2))
        return
    fw = data[FW_OFFSET:] if len(data) > FW_OFFSET else b""
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "eeprom_size": len(data),
        "firmware_offset": FW_OFFSET,
        "firmware_scan": scan_firmware(fw, source),
    }
    if source == "synthetic_reference":
        meta["warning"] = "NOT device firmware"
    out = ROOT / "manifests" / "firmware_scan.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
