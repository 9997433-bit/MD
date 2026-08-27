#!/usr/bin/env python3
"""Scan firmware from real EEPROM or synthetic fixture."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_parse import parse_eeprom  # noqa: E402
from eeprom_source import resolve_eeprom_path  # noqa: E402

# 8051 opcode names for frequency histogram (subset)
OPCODES = {
    0x00: "NOP",
    0x02: "LJMP",
    0x12: "LCALL",
    0x22: "RET",
    0x32: "RETI",
    0x74: "MOV A,#",
    0x75: "MOV direct,#",
    0x90: "MOV DPTR,#",
}


def scan_firmware(fw: bytes, source: str) -> dict:
    if len(fw) < 4:
        return {"status": "too_short", "size": len(fw), "source": source}
    hist: dict[str, int] = {}
    for b in fw[:512]:
        name = OPCODES.get(b, f"0x{b:02x}")
        hist[name] = hist.get(name, 0) + 1
    top = sorted(hist.items(), key=lambda x: -x[1])[:8]
    observed = source == "device_capture"
    return {
        "status": "observed" if observed else "synthetic_pipeline_test",
        "source": source,
        "size_bytes": len(fw),
        "header_hex": fw[:32].hex(),
        "opcode_histogram_top8": dict(top),
        "boundary": "Histogram only; use Ghidra 8051 for real disassembly",
    }


def main() -> None:
    path, kind = resolve_eeprom_path()
    if path is None:
        meta = {"status": "missing", "path": "phase_b/captures/eeprom.bin"}
        (ROOT / "manifests" / "firmware_scan.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(json.dumps(meta, indent=2))
        return

    data = path.read_bytes()
    hdr = parse_eeprom(data)
    if hdr.firmware_offset is None or hdr.firmware_size_bytes is None:
        fw = b""
    else:
        fw = data[hdr.firmware_offset : hdr.firmware_offset + hdr.firmware_size_bytes]

    scan_source = "device_capture" if kind == "device_capture" else kind
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "eeprom_size": len(data),
        "boot_format": hdr.boot_format,
        "firmware_offset": hdr.firmware_offset,
        "firmware_scan": scan_firmware(fw, scan_source),
    }
    if kind != "device_capture":
        meta["warning"] = "NOT device firmware"
    out = ROOT / "manifests" / "firmware_scan.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
