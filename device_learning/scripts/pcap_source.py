"""Detect synthetic USB capture fixtures vs real pcapng in captures/."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH_ENUM = ROOT / "phase_b" / "fixtures" / "usb_enum_synthetic_reference.pcapng"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def synthetic_sha256(name: str = "usb_enum_synthetic_reference.pcapng") -> str | None:
    path = ROOT / "phase_b" / "fixtures" / name
    if not path.exists():
        return None
    return sha256_file(path)


def is_synthetic_pcap(data: bytes) -> bool:
    ref = synthetic_sha256()
    if ref is None:
        return False
    return sha256_bytes(data) == ref
