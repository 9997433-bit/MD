#!/usr/bin/env python3
"""Ingest phase B capture artifacts (stub)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"


def main() -> None:
    CAPTURES.mkdir(parents=True, exist_ok=True)
    found = [n for n in ("eeprom.bin", "usb_enum.pcapng", "usb_session.pcapng") if (CAPTURES / n).exists()]
    status = {"captures_found": found, "ready": "eeprom.bin" in found}
    out = ROOT / "manifests" / "phase_b_status.json"
    out.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
