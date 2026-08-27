#!/usr/bin/env python3
"""Analyze a serial-EEPROM boot image against the public layout reference.

If ``phase_b/captures/eeprom.bin`` exists, parse the fields the public boot
format defines (boot-config byte, VID/PID identifier offsets, and — for a C2
firmware image — the firmware size implied by the data records) and write
``manifests/eeprom_meta.json``. If no dump is present, write a ``missing``
status instead so downstream tools record the honest gap rather than guessing.

Offsets are taken from ``manifests/eeprom_layout_ref.json`` (public datasheet
reference), never from any assumed device-specific value. Uses neutral naming
and does not reference any specific product model.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "phase_b" / "captures" / "eeprom.bin"
LAYOUT_REF = ROOT / "manifests" / "eeprom_layout_ref.json"
OUT = ROOT / "manifests" / "eeprom_meta.json"

FINAL_RECORD_FLAG = 0x8000
RESET_CONTROL_ADDR = 0xE600


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _field_offsets(layout: dict) -> dict[str, int]:
    offsets: dict[str, int] = {}
    for field in layout.get("fields", []):
        off = field.get("offset")
        if isinstance(off, int):
            offsets[field["name"]] = off
    return offsets


def _write(meta: dict) -> None:
    OUT.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2, ensure_ascii=False))


def _missing_meta(reason: str) -> dict:
    return {
        "generated_at": _now(),
        "capture_path": CAPTURE.relative_to(ROOT).as_posix(),
        "status": "missing",
        "reason": reason,
        "layout_ref": LAYOUT_REF.relative_to(ROOT).as_posix(),
        "note": "no EEPROM dump available; no field values inferred",
    }


def _parse_c2_firmware(data: bytes) -> dict:
    """Walk C2 data records to derive firmware size; never raise on bad data."""
    pos = 8
    records = 0
    payload_bytes = 0
    end_pos = pos
    truncated = False
    reset_release_seen = False
    while pos + 4 <= len(data):
        length_word = int.from_bytes(data[pos:pos + 2], "big")
        address = int.from_bytes(data[pos + 2:pos + 4], "big")
        payload_len = length_word & 0x7FFF
        is_final = bool(length_word & FINAL_RECORD_FLAG)
        body_start = pos + 4
        body_end = body_start + payload_len
        if body_end > len(data):
            truncated = True
            break
        records += 1
        pos = body_end
        end_pos = pos
        if is_final:
            reset_release_seen = address == RESET_CONTROL_ADDR
            break
        payload_bytes += payload_len
    return {
        "record_count": records,
        "firmware_payload_bytes": payload_bytes,
        "image_span_bytes": end_pos,
        "records_truncated": truncated,
        "reset_release_record": reset_release_seen,
    }


def analyze(data: bytes, layout: dict) -> dict:
    offsets = _field_offsets(layout)
    boot_off = offsets.get("boot_config_byte", 0)
    vid_off = offsets.get("vid", 1)
    pid_off = offsets.get("pid", 3)
    did_off = offsets.get("did", 5)
    cfg_off = offsets.get("config_byte", 7)

    boot_byte = data[boot_off] if len(data) > boot_off else None
    if boot_byte == 0xC0:
        boot_format = "C0"
    elif boot_byte == 0xC2:
        boot_format = "C2"
    else:
        boot_format = "unrecognized"

    def le16(off: int):
        return int.from_bytes(data[off:off + 2], "little") if off + 2 <= len(data) else None

    meta = {
        "generated_at": _now(),
        "capture_path": CAPTURE.relative_to(ROOT).as_posix(),
        "status": "parsed",
        "layout_ref": LAYOUT_REF.relative_to(ROOT).as_posix(),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "boot_config_byte": None if boot_byte is None else f"0x{boot_byte:02X}",
        "boot_format": boot_format,
        "identifiers": {
            "vid_offset": vid_off,
            "vid_offset_hex": f"0x{vid_off:02X}",
            "vid": None if le16(vid_off) is None else f"0x{le16(vid_off):04X}",
            "pid_offset": pid_off,
            "pid_offset_hex": f"0x{pid_off:02X}",
            "pid": None if le16(pid_off) is None else f"0x{le16(pid_off):04X}",
            "did_offset": did_off,
            "did": None if le16(did_off) is None else f"0x{le16(did_off):04X}",
        },
        "config_byte": (
            f"0x{data[cfg_off]:02X}" if len(data) > cfg_off else None
        ),
    }

    if boot_format == "C2":
        meta["firmware"] = _parse_c2_firmware(data)
    else:
        meta["firmware"] = {
            "note": "no C2 firmware records for this boot format",
            "firmware_payload_bytes": 0,
        }
    return meta


def main() -> None:
    if not LAYOUT_REF.is_file():
        _write(_missing_meta(f"layout reference not found: {LAYOUT_REF.name}"))
        return
    layout = json.loads(LAYOUT_REF.read_text(encoding="utf-8"))

    if not CAPTURE.is_file():
        _write(_missing_meta("phase_b/captures/eeprom.bin not present"))
        return

    data = CAPTURE.read_bytes()
    if not data:
        _write(_missing_meta("phase_b/captures/eeprom.bin is empty"))
        return

    _write(analyze(data, layout))


if __name__ == "__main__":
    main()
