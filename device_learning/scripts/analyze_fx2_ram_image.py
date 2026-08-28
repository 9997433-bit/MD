#!/usr/bin/env python3
"""Scan FX2 RAM image reconstructed from USB enum (NOT eeprom.bin).

Writes manifests/fx2_ram_scan.json. Requires phase_b/analysis/fx2_ram_from_enum.bin.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
OUT = ROOT / "manifests" / "fx2_ram_scan.json"

OPCODES = {
    0x00: "NOP",
    0x02: "LJMP",
    0x12: "LCALL",
    0x22: "RET",
    0x32: "RETI",
    0x74: "MOV_A_imm",
    0x75: "MOV_dir_imm",
    0x80: "SJMP",
    0x90: "MOV_DPTR_imm",
}


def printable_strings(data: bytes, min_len: int = 4) -> list[dict]:
    out: list[dict] = []
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data):
        s = m.group().decode("ascii", errors="replace")
        out.append({"offset": f"0x{m.start():04x}", "text": s})
    return out[:40]


def reset_vector_hint(data: bytes) -> dict:
    if len(data) < 3:
        return {"status": "too_short"}
    b0 = data[0]
    if b0 == 0x02 and len(data) >= 3:
        dest = (data[1] << 8) | data[2]
        return {
            "byte0": "0x02",
            "interpretation": "LJMP abs",
            "target": f"0x{dest:04x}",
            "confidence": "candidate",
        }
    return {
        "byte0": f"0x{b0:02x}",
        "interpretation": "not classic LJMP-at-0",
        "header_hex": data[:16].hex(),
        "confidence": "hypothesis",
    }


def opcode_hist(data: bytes, nbytes: int = 2048) -> dict[str, int]:
    hist: Counter[str] = Counter()
    for b in data[:nbytes]:
        hist[OPCODES.get(b, f"0x{b:02x}")] += 1
    return dict(hist.most_common(12))


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        report = {
            "generated_at": now,
            "status": "missing",
            "path": str(RAM.relative_to(ROOT)),
            "boundary": "Run FX2 RAM extract from usb_enum first",
            "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        }
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    data = RAM.read_bytes()
    strings = printable_strings(data)
    # USB string-like / VID hints
    interesting = [s for s in strings if any(k in s["text"].lower() for k in ("usb", "fx2", "ni", "corp", "serial", "bulk"))]

    report = {
        "generated_at": now,
        "status": "scanned",
        "confidence": "candidate",
        "path": str(RAM.relative_to(ROOT)),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "source_note": "Volatile FX2-style RAM load from usb_enum.pcapng — NOT eeprom.bin",
        "reset_vector_hint": reset_vector_hint(data),
        "opcode_histogram_first_2kib": opcode_hist(data),
        "zero_ratio": round(data.count(0) / max(1, len(data)), 4),
        "unique_bytes": len(set(data)),
        "strings_ascii_top": strings[:20],
        "strings_interesting": interesting[:15],
        "boundary": "Histogram/strings only; full 8051 disasm still needs Ghidra + preferably persistent EEPROM",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "size": report["size_bytes"],
                "reset": report["reset_vector_hint"],
                "string_count": len(strings),
                "interesting": len(interesting),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
