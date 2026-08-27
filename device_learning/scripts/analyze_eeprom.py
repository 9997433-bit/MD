#!/usr/bin/env python3
"""Analyze EEPROM: real capture preferred, synthetic fixture fallback for pipeline test."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_parse import parse_eeprom  # noqa: E402

REAL = ROOT / "phase_b" / "captures" / "eeprom.bin"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"


def analyze(path: Path, source: str) -> dict:
    data = path.read_bytes()
    hdr = parse_eeprom(data)
    return {
        "source": source,
        "path": str(path.relative_to(ROOT)),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "boot_format": hdr.boot_format,
        "boot_config_byte": f"0x{hdr.boot_config_byte:02x}",
        "vid_hex": f"0x{hdr.vid:04x}" if hdr.vid is not None else None,
        "pid_hex": f"0x{hdr.pid:04x}" if hdr.pid is not None else None,
        "did_hex": f"0x{hdr.did:04x}" if hdr.did is not None else None,
        "config_byte": f"0x{hdr.config_byte:02x}" if hdr.config_byte is not None else None,
        "firmware_offset": hdr.firmware_offset,
        "firmware_size_bytes": hdr.firmware_size_bytes,
        "firmware_header_hex": hdr.firmware_header_hex,
        "c2_record_count": hdr.c2_record_count,
        "layout_ref": "manifests/eeprom_layout_ref.json",
        "boundary": "Values observed from file only; synthetic fixture is NOT device truth",
    }


def main() -> None:
    if REAL.exists():
        meta = {"status": "observed", "generated_at": datetime.now(timezone.utc).isoformat(), **analyze(REAL, "device_capture")}
    elif SYNTH.exists():
        meta = {
            "status": "synthetic_pipeline_test",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "warning": "Using synthetic fixture — NOT device data",
            **analyze(SYNTH, "synthetic_reference"),
        }
    else:
        meta = {
            "status": "missing",
            "path": str(REAL.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "note": "Run build_eeprom_synthetic.py or provide real eeprom.bin",
        }
    out = ROOT / "manifests" / "eeprom_meta.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
