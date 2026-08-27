#!/usr/bin/env python3
"""Validate catalog entry schema and identifier uniqueness."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_arch import ENTRIES as ARCH
from catalogs.catalog_bit import ENTRIES as BIT
from catalogs.catalog_exp import ENTRIES as EXP
from catalogs.catalog_hw import ENTRIES as HW
from catalogs.catalog_learn import ENTRIES as LEARN
from catalogs.catalog_ref import ENTRIES as REF
from catalogs.catalog_signal import ENTRIES as SIG
from catalogs.catalog_usb import ENTRIES as USB

ALL = HW + BIT + SIG + USB + REF + ARCH + LEARN + EXP
REQUIRED_KEYS = ("identifier", "layer", "module", "description", "status")
VALID_STATUS = {"confirmed", "candidate", "unknown", "hypothesis", "not_started", "missing"}


def main() -> None:
    issues: list[str] = []
    seen: dict[str, int] = {}
    for e in ALL:
        iid = e.get("identifier", "")
        seen[iid] = seen.get(iid, 0) + 1
        for k in REQUIRED_KEYS:
            if not e.get(k):
                issues.append(f"{iid}: missing key {k}")
        if e.get("status") not in VALID_STATUS:
            issues.append(f"{iid}: invalid status {e.get('status')}")

    dupes = [k for k, v in seen.items() if v > 1]
    if dupes:
        issues.append(f"duplicate identifiers: {dupes}")

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entry_count": len(ALL),
        "unique_identifiers": len(seen),
        "duplicate_count": len(dupes),
        "issue_count": len(issues),
        "issues": issues[:50],
        "ok": len(issues) == 0,
    }
    out = ROOT / "manifests" / "catalog_integrity.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": meta["ok"], "entry_count": meta["entry_count"]}, indent=2))
    if not meta["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
