#!/usr/bin/env python3
"""Summarize USB capture files when present (no protocol decode without hardware)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sniff_pcap_magic(data: bytes) -> str:
    if len(data) < 4:
        return "too_short"
    if data[:4] == b"\xd4\xc3\xb2\xa1":
        return "pcap_le"
    if data[:4] == b"\xa1\xb2\xc3\xd4":
        return "pcap_be"
    if data[:4] == b"\x0a\x0d\x0d\x0a":
        return "pcapng"
    return "unknown"


def main() -> None:
    pcaps = sorted(
        p for p in CAPTURES.glob("*") if p.is_file() and p.suffix in (".pcap", ".pcapng")
    )
    if not pcaps:
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "missing",
            "path": str(CAPTURES.relative_to(ROOT)),
            "boundary": "No USB capture yet; place *.pcapng in phase_b/captures/",
        }
    else:
        files = []
        for p in pcaps:
            head = p.read_bytes()[:16]
            files.append(
                {
                    "name": p.name,
                    "size_bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                    "magic": sniff_pcap_magic(head),
                }
            )
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "observed",
            "capture_count": len(files),
            "files": files,
            "boundary": "File metadata only; endpoint/protocol decode requires Wireshark + device",
        }

    out = ROOT / "manifests" / "usb_capture_meta.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
