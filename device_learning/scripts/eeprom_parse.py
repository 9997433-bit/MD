#!/usr/bin/env python3
"""Shared FX2LP serial-EEPROM layout parser (public datasheet offsets only)."""
from __future__ import annotations

from dataclasses import dataclass

BOOT_C0 = 0xC0
BOOT_C2 = 0xC2


@dataclass
class EepromHeader:
    boot_format: str
    boot_config_byte: int
    vid: int | None
    pid: int | None
    did: int | None
    config_byte: int | None
    firmware_offset: int | None
    firmware_size_bytes: int | None
    firmware_header_hex: str | None
    c2_record_count: int


def parse_eeprom(data: bytes) -> EepromHeader:
    if not data:
        return EepromHeader("empty", 0, None, None, None, None, None, None, None, 0)

    boot = data[0]
    vid = int.from_bytes(data[1:3], "little") if len(data) >= 3 else None
    pid = int.from_bytes(data[3:5], "little") if len(data) >= 5 else None
    did = int.from_bytes(data[5:7], "little") if len(data) >= 7 else None
    cfg = data[7] if len(data) >= 8 else None

    if boot == BOOT_C0:
        return EepromHeader("C0", boot, vid, pid, did, cfg, None, None, None, 0)

    if boot == BOOT_C2:
        offset = 8
        records = 0
        fw_offset = None
        fw_size = None
        fw_header = None
        while offset + 4 <= len(data):
            length = int.from_bytes(data[offset : offset + 2], "big")
            address = int.from_bytes(data[offset + 2 : offset + 4], "big")
            payload_len = length & 0x7FFF
            if length & 0x8000:
                payload_len = 1
            end = offset + 4 + payload_len
            if end > len(data):
                break
            payload = data[offset + 4 : end]
            records += 1
            if fw_offset is None and payload_len > 0:
                fw_offset = offset + 4
                fw_size = payload_len
                fw_header = payload[:32].hex()
            if length & 0x8000:
                break
            offset = end
        return EepromHeader(
            "C2", boot, vid, pid, did, cfg, fw_offset, fw_size, fw_header, records
        )

    return EepromHeader("ignored", boot, None, None, None, None, None, None, None, 0)
