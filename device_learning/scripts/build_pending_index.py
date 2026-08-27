#!/usr/bin/env python3
"""Build an index of identifiers still blocked on hardware or deeper decode."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_arch import ENTRIES as ARCH_ENTRIES
from catalogs.catalog_bit import ENTRIES as BIT_ENTRIES
from catalogs.catalog_exp import ENTRIES as EXP_ENTRIES
from catalogs.catalog_hw import ENTRIES as HW_ENTRIES
from catalogs.catalog_learn import ENTRIES as LEARN_ENTRIES
from catalogs.catalog_ref import ENTRIES as REF_ENTRIES
from catalogs.catalog_signal import ENTRIES as SIG_ENTRIES
from catalogs.catalog_usb import ENTRIES as USB_ENTRIES

BLOCKED_STATUSES = ("missing", "not_started", "unknown")
CATALOGS = {
    "hw": HW_ENTRIES,
    "bit": BIT_ENTRIES,
    "signal": SIG_ENTRIES,
    "usb": USB_ENTRIES,
    "ref": REF_ENTRIES,
    "arch": ARCH_ENTRIES,
    "learn": LEARN_ENTRIES,
    "exp": EXP_ENTRIES,
}


def main() -> None:
    by_status: dict[str, list[dict]] = defaultdict(list)
    by_layer: dict[str, list[dict]] = defaultdict(list)

    for layer, entries in CATALOGS.items():
        for e in entries:
            item = {
                "identifier": e["identifier"],
                "layer": layer,
                "status": e["status"],
                "boundary": e.get("boundary"),
                "module": e.get("module"),
            }
            if e["status"] in BLOCKED_STATUSES:
                by_status[e["status"]].append(item)
                by_layer[layer].append(item)

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blocked_statuses": list(BLOCKED_STATUSES),
        "total_blocked": sum(len(v) for v in by_status.values()),
        "by_status": {k: {"count": len(v), "items": v} for k, v in sorted(by_status.items())},
        "by_layer": {k: {"count": len(v), "identifiers": [x["identifier"] for x in v]} for k, v in sorted(by_layer.items())},
        "phase_b_unblocks": [
            i["identifier"]
            for i in by_status.get("missing", []) + by_status.get("not_started", [])
            if i["layer"] in ("usb", "signal", "learn", "exp")
        ],
        "note": "Blocked items must not be upgraded without new evidence",
    }

    out = ROOT / "manifests" / "pending_index.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"total_blocked": meta["total_blocked"]}, indent=2))


if __name__ == "__main__":
    main()
