#!/usr/bin/env python3
"""Audit text artifacts for sensitive tokens that must not appear in manifests/docs."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "manifests", ROOT]
SCAN_GLOBS = ("*.json", "*.md")
SKIP_FILES = {"device.bit", "EvidenceLedger.json", "sensitive_audit.json"}
PATTERNS = [
    ("PAT_TOPUSB", re.compile(r"topusb", re.I)),
    ("PAT_PRODUCT_DIGIT", re.compile(r"4431")),
]


def scan_file(path: Path) -> list[dict]:
    if path.name in SKIP_FILES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    hits = []
    for label, pat in PATTERNS:
        for m in pat.finditer(text):
            hits.append({"pattern_id": label, "offset": m.start()})
    return hits


def main() -> None:
    findings: list[dict] = []
    for base in SCAN_DIRS:
        for glob in SCAN_GLOBS:
            for path in base.glob(glob):
                if path.is_file() and path.suffix in (".json", ".md"):
                    hits = scan_file(path)
                    if hits:
                        findings.append({"file": str(path.relative_to(ROOT)), "hits": hits[:5]})

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanned_roots": [str(d.relative_to(ROOT)) for d in SCAN_DIRS],
        "finding_count": len(findings),
        "findings": findings,
        "ok": len(findings) == 0,
    }
    out = ROOT / "manifests" / "sensitive_audit.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": meta["ok"], "finding_count": meta["finding_count"]}, indent=2))
    if not meta["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
