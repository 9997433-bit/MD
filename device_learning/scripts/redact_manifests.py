#!/usr/bin/env python3
"""Redact sensitive tokens from manifest JSON files."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "manifests"

# Patterns to redact in string values (product-specific tokens user asked to omit)
REDACT_PATTERNS = [
    (re.compile(r"TopUsb\d+\.ncd", re.I), "[redacted].ncd"),
    (re.compile(r"Usb\d+", re.I), "[redacted]"),
    (re.compile(r"4431"), "[redacted]"),
]


def redact_obj(obj):
    if isinstance(obj, str):
        s = obj
        for pat, repl in REDACT_PATTERNS:
            s = pat.sub(repl, s)
        return s
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    return obj


def main() -> None:
    for path in MANIFESTS.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        cleaned = redact_obj(data)
        path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"redacted {len(list(MANIFESTS.glob('*.json')))} manifest files")


if __name__ == "__main__":
    main()
