#!/usr/bin/env python3
"""Extract 8051 firmware slice from real eeprom.bin for Ghidra import."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_parse import parse_eeprom  # noqa: E402
from eeprom_source import is_synthetic_dump, sha256_bytes  # noqa: E402

REAL = ROOT / "phase_b" / "captures" / "eeprom.bin"
DEFAULT_OUT = ROOT / "phase_b" / "analysis" / "firmware.bin"
META_OUT = ROOT / "manifests" / "firmware_extract.json"


def extract(data: bytes, source: str) -> dict:
    hdr = parse_eeprom(data)
    if hdr.boot_format == "C0":
        return {
            "status": "no_firmware_image",
            "boot_format": hdr.boot_format,
            "boundary": "C0 boot format has no onboard firmware records",
            "source": source,
        }
    if hdr.firmware_offset is None or hdr.firmware_size_bytes is None:
        return {
            "status": "no_firmware_slice",
            "boot_format": hdr.boot_format,
            "boundary": "Could not locate C2 data-record payload",
            "source": source,
        }
    fw = data[hdr.firmware_offset : hdr.firmware_offset + hdr.firmware_size_bytes]
    return {
        "status": "extracted",
        "boot_format": hdr.boot_format,
        "source": source,
        "firmware_offset": hdr.firmware_offset,
        "firmware_size_bytes": len(fw),
        "sha256": sha256_bytes(fw),
        "header_hex": fw[:32].hex(),
        "payload": fw,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract firmware slice from eeprom.bin")
    parser.add_argument("-i", "--input", default=str(REAL), help="EEPROM dump path")
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUT), help="Firmware binary output")
    parser.add_argument("--allow-synthetic", action="store_true", help="Allow synthetic fixture (test only)")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        meta = {"status": "missing", "path": str(src), "generated_at": datetime.now(timezone.utc).isoformat()}
        META_OUT.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(meta, indent=2))
        return 1

    source = "device_capture"
    data = src.read_bytes()
    if is_synthetic_dump(data):
        source = "synthetic_reference"
        if not args.allow_synthetic:
            meta = {
                "status": "rejected",
                "reason": "EEPROM SHA-256 matches synthetic fixture; pass --allow-synthetic for pipeline test",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            META_OUT.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(meta, indent=2), file=sys.stderr)
            return 2

    result = extract(data, source)
    payload = result.pop("payload", None)
    result["generated_at"] = datetime.now(timezone.utc).isoformat()
    result["input"] = str(src.relative_to(ROOT) if src.is_relative_to(ROOT) else src)

    if result["status"] == "extracted" and payload is not None:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(payload)
        result["output"] = str(out.relative_to(ROOT) if out.is_relative_to(ROOT) else out)
        if source == "synthetic_reference":
            result["warning"] = "NOT device firmware"

    META_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "payload"}, indent=2))
    return 0 if result["status"] == "extracted" else 3


if __name__ == "__main__":
    sys.exit(main())
