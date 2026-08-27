#!/usr/bin/env python3
"""Map hardware photos to HW catalog identifiers via photo_index."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KEYWORD_TO_HW = [
    (r"SPARTAN|XC3S200|FPGA", ["HW-001-FPGA-DEVICE", "HW-002-FPGA-PACKAGE"]),
    (r"CY7C68013|USB", ["HW-003-USB-CONTROLLER", "HW-017-INTERFACE-USB"]),
    (r"G6JU|继电器", ["HW-008-RELAY-ARRAY", "HW-009-RELAY-COUNT"]),
    (r"1271|ADS127|ADC|模数", ["HW-005-ADC-PRIMARY", "HW-006-ADC-COUNT"]),
    (r"KS245", ["HW-011-BUS-TRANSCEIVER"]),
    (r"ISSI|SRAM", ["HW-023-MEMORY-SRAM"]),
    (r"24\.000M|24M", ["HW-014-CRYSTAL-USB"]),
    (r"BNC|同轴", ["HW-016-INTERFACE-COAX"]),
    (r"198755F", ["HW-019-BOARD-REVISION"]),
    (r"COPYRIGHT|2011", ["HW-025-COPYRIGHT-YEAR"]),
    (r"CE", ["HW-030-COMPLIANCE"]),
]


def match_hw(text: str) -> list[str]:
    hits: list[str] = []
    upper = text.upper()
    for pat, ids in KEYWORD_TO_HW:
        if re.search(pat, upper, re.I):
            hits.extend(ids)
    return sorted(set(hits))


def main() -> None:
    photos = json.loads((ROOT / "manifests" / "photo_index.json").read_text(encoding="utf-8"))
    mapped = []
    for photo in photos.get("photos", []):
        blob = json.dumps(photo.get("components", []), ensure_ascii=False)
        hw_ids = match_hw(blob)
        mapped.append(
            {
                "file": photo["file"],
                "component_count": photo.get("component_count", 0),
                "hw_identifiers": hw_ids,
            }
        )

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "photo_count": photos.get("photo_count", 0),
        "photos_with_hw_links": sum(1 for p in mapped if p["hw_identifiers"]),
        "photos": mapped,
        "boundary": "Keyword match on photo_index components only",
    }
    out = ROOT / "manifests" / "photo_hw_map.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"photos_with_hw_links": meta["photos_with_hw_links"]}, indent=2))


if __name__ == "__main__":
    main()
