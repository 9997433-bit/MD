#!/usr/bin/env python3
"""Build per-photo component index from hardware BOM."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    bom = json.loads((ROOT / "manifests" / "hardware_bom.json").read_text(encoding="utf-8"))
    by_photo: dict[str, list[dict]] = defaultdict(list)
    for comp in bom.get("components", []):
        for photo in comp.get("photo_source", []):
            by_photo[photo].append({
                "ref": comp.get("ref_designator"),
                "marking": comp.get("part_marking"),
                "function": comp.get("function"),
                "status": comp.get("status"),
            })
    photos = []
    for name in bom.get("source_photos", sorted(by_photo.keys())):
        items = by_photo.get(name, [])
        photos.append({
            "file": name,
            "component_count": len(items),
            "components": items,
        })
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "photo_count": len(photos),
        "photos": photos,
    }
    path = ROOT / "manifests" / "photo_index.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"photo_index: {len(photos)} photos, {sum(p['component_count'] for p in photos)} refs")


if __name__ == "__main__":
    main()
