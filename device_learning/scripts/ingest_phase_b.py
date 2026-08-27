#!/usr/bin/env python3
"""Ingest phase B capture artifacts and record metadata for ledger refresh."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_source import is_synthetic_dump  # noqa: E402
from pcap_source import is_synthetic_pcap  # noqa: E402
CAPTURES = ROOT / "phase_b" / "captures"
EXPECTED_EEPROM_SIZE = 8192  # 24LC64


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def describe_capture(path: Path) -> dict:
    info: dict = {
        "name": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if path.name == "eeprom.bin":
        info["expected_size_bytes"] = EXPECTED_EEPROM_SIZE
        info["size_match"] = info["size_bytes"] == EXPECTED_EEPROM_SIZE
        info["is_synthetic_fixture"] = is_synthetic_dump(path.read_bytes())
    if path.suffix in (".pcap", ".pcapng"):
        info["type"] = "usb_capture"
        info["is_synthetic_fixture"] = is_synthetic_pcap(path.read_bytes())
    if path.name == "protocol_log.json":
        info["type"] = "protocol_log"
        try:
            info["protocol_entries"] = len(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            info["protocol_entries"] = None
    return info


def main() -> None:
    CAPTURES.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in CAPTURES.iterdir() if p.is_file() and not p.name.startswith("."))
    captures = [describe_capture(p) for p in files]

    has_eeprom = any(c["name"] == "eeprom.bin" for c in captures)
    has_real_eeprom = any(
        c["name"] == "eeprom.bin" and not c.get("is_synthetic_fixture") for c in captures
    )
    has_pcap = any(c.get("type") == "usb_capture" for c in captures)
    has_real_pcap = any(
        c.get("type") == "usb_capture" and not c.get("is_synthetic_fixture") for c in captures
    )
    has_protocol = any(c.get("type") == "protocol_log" for c in captures)

    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "captures_dir": str(CAPTURES.relative_to(ROOT)),
        "capture_count": len(captures),
        "captures": captures,
        "flags": {
            "eeprom_present": has_eeprom,
            "eeprom_observed": has_real_eeprom,
            "usb_capture_present": has_pcap,
            "usb_capture_observed": has_real_pcap,
            "protocol_log_present": has_protocol,
        },
        "ready_for_ledger_refresh": has_real_eeprom or has_real_pcap,
        "next_steps": [],
    }
    if not captures:
        status["next_steps"].append("Place eeprom.bin and/or *.pcapng in phase_b/captures/")
    if has_eeprom:
        status["next_steps"].append("Run generate_ledger.py to refresh FW layer from real dump")
    if has_pcap:
        status["next_steps"].append("Run analyze_pcap_stub.py then generate_ledger.py")

    out = ROOT / "manifests" / "phase_b_status.json"
    out.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
