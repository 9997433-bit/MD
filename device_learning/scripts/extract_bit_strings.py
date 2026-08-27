#!/usr/bin/env python3
"""Extract printable ASCII strings from the bitstream payload (redacted output)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIT = ROOT / "firmware" / "device.bit"
MIN_LEN = 4

REDACT_PATTERNS = [
    (re.compile(r"TopUsb\d+\.ncd", re.I), "[redacted].ncd"),
    (re.compile(r"Usb\d+", re.I), "[redacted]"),
    (re.compile(r"4431"), "[redacted]"),
]


def redact(s: str) -> str:
    out = s
    for pat, repl in REDACT_PATTERNS:
        out = pat.sub(repl, out)
    return out


def extract_strings(data: bytes, min_len: int = MIN_LEN) -> list[str]:
    found: list[str] = []
    current: list[int] = []
    for b in data:
        if 32 <= b < 127:
            current.append(b)
        else:
            if len(current) >= min_len:
                found.append(bytes(current).decode("ascii"))
            current = []
    if len(current) >= min_len:
        found.append(bytes(current).decode("ascii"))
    return found


def main() -> None:
    if not BIT.exists():
        meta = {"status": "missing", "path": str(BIT)}
    else:
        raw = BIT.read_bytes()
        # Skip Xilinx header section 'e' payload starts after ~94 bytes; scan whole file for safety
        strings = extract_strings(raw)
        redacted = sorted({redact(s) for s in strings})
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(BIT.relative_to(ROOT)),
            "file_size_bytes": len(raw),
            "min_string_length": MIN_LEN,
            "raw_string_count": len(strings),
            "unique_redacted_count": len(redacted),
            "strings_redacted": redacted[:80],
            "truncated": len(redacted) > 80,
            "boundary": "Heuristic ASCII scan; redacted before manifest write",
        }

    out = ROOT / "manifests" / "bit_strings.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"unique_redacted_count": meta.get("unique_redacted_count", 0)}, indent=2))


if __name__ == "__main__":
    main()
