#!/usr/bin/env python3
"""Compare two EEPROM dumps for byte-level consistency (phase B QA)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_parse import parse_eeprom  # noqa: E402


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compare(a: bytes, b: bytes) -> dict:
    mismatches = []
    limit = min(len(a), len(b))
    for i in range(limit):
        if a[i] != b[i]:
            mismatches.append({"offset": i, "a": f"0x{a[i]:02x}", "b": f"0x{b[i]:02x}"})
            if len(mismatches) >= 20:
                break
    return {
        "size_a": len(a),
        "size_b": len(b),
        "size_match": len(a) == len(b),
        "sha256_a": hashlib.sha256(a).hexdigest(),
        "sha256_b": hashlib.sha256(b).hexdigest(),
        "identical": a == b,
        "mismatch_count": sum(1 for i in range(limit) if a[i] != b[i]),
        "first_mismatches": mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two EEPROM dump files")
    parser.add_argument("file_a")
    parser.add_argument("file_b")
    parser.add_argument("-o", "--out", default=str(ROOT / "manifests" / "eeprom_diff.json"))
    args = parser.parse_args()

    pa, pb = Path(args.file_a), Path(args.file_b)
    da, db = pa.read_bytes(), pb.read_bytes()
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_a": str(pa),
        "file_b": str(pb),
        "compare": compare(da, db),
        "header_a": parse_eeprom(da).__dict__,
        "header_b": parse_eeprom(db).__dict__,
    }
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"identical": result["compare"]["identical"]}, indent=2))


if __name__ == "__main__":
    main()
