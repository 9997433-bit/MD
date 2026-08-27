#!/usr/bin/env python3
"""Analyze EEPROM: real capture preferred, synthetic fixture fallback for pipeline test."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "phase_b" / "captures" / "eeprom.bin"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"
FW_OFFSET = 0x10


def analyze(path: Path, source: str) -> dict:
    data = path.read_bytes()
    boot = data[0] if data else None
    vid = int.from_bytes(data[8:10], "little") if len(data) >= 10 else None
    pid = int.from_bytes(data[10:12], "little") if len(data) >= 12 else None
    fw = data[FW_OFFSET:] if len(data) > FW_OFFSET else b""
    return {
        "source": source,
        "path": str(path.relative_to(ROOT)),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "boot_config_byte": f"0x{boot:02x}" if boot is not None else None,
        "vid_hex": f"0x{vid:04x}" if vid is not None else None,
        "pid_hex": f"0x{pid:04x}" if pid is not None else None,
        "firmware_offset": FW_OFFSET,
        "firmware_size_bytes": len(fw),
        "firmware_header_hex": fw[:32].hex() if fw else None,
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
