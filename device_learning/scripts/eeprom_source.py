"""Shared helpers for distinguishing real EEPROM captures from synthetic fixtures."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "phase_b" / "captures" / "eeprom.bin"
SYNTH = ROOT / "phase_b" / "fixtures" / "eeprom_synthetic_reference.bin"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def synthetic_sha256() -> str | None:
    if not SYNTH.exists():
        return None
    return sha256_file(SYNTH)


def is_synthetic_dump(data: bytes) -> bool:
    ref = synthetic_sha256()
    if ref is None:
        return False
    return sha256_bytes(data) == ref


def resolve_eeprom_path() -> tuple[Path | None, str]:
    """Return (path, source_kind) where source_kind is device_capture, synthetic_reference, or missing."""
    if REAL.exists():
        data = REAL.read_bytes()
        if is_synthetic_dump(data):
            return REAL, "synthetic_in_captures"
        return REAL, "device_capture"
    if SYNTH.exists():
        return SYNTH, "synthetic_reference"
    return None, "missing"
