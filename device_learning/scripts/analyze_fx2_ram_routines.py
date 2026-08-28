#!/usr/bin/env python3
"""L3 routine segmentation heuristics on fx2_ram_from_enum.bin.

Splits the image using RET(0x22)/RETI(0x32) terminators and absolute call
targets as likely entries. Writes manifests/fx2_ram_routines.json.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
XREFS = ROOT / "manifests" / "fx2_ram_xrefs.json"
OUT = ROOT / "manifests" / "fx2_ram_routines.json"


def abs_targets(data: bytes) -> Counter[int]:
    c: Counter[int] = Counter()
    for i in range(len(data) - 2):
        if data[i] in (0x02, 0x12):  # LJMP / LCALL
            dest = (data[i + 1] << 8) | data[i + 2]
            if dest < len(data):
                c[dest] += 1
    return c


def segment(data: bytes, entries: list[int]) -> list[dict]:
    """Build [entry, next_entry) ranges; trim trailing zeros lightly."""
    entries = sorted(set(entries))
    routines = []
    for idx, start in enumerate(entries):
        end = entries[idx + 1] if idx + 1 < len(entries) else len(data)
        body = data[start:end]
        # find last RET/RETI in body
        last_ret = None
        for j in range(len(body) - 1, -1, -1):
            if body[j] in (0x22, 0x32):
                last_ret = start + j
                break
        routines.append(
            {
                "entry": f"0x{start:04x}",
                "end_exclusive": f"0x{end:04x}",
                "size_bytes": end - start,
                "last_ret": f"0x{last_ret:04x}" if last_ret is not None else None,
                "ends_with_ret": body[-1] in (0x22, 0x32) if body else False,
            }
        )
    return routines


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        report = {"generated_at": now, "status": "missing", "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为"}
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    data = RAM.read_bytes()
    targets = abs_targets(data)
    # Seed entries: reset target 0x075b if present, hot call targets, and 0x0000
    seeds = {0x0000}
    if len(data) >= 3 and data[0] == 0x02:
        seeds.add((data[1] << 8) | data[2])
    # hot destinations with >=3 refs
    seeds.update(d for d, n in targets.items() if n >= 3)
    # also include every LCALL/LJMP dest with >=2 for denser map
    seeds.update(d for d, n in targets.items() if n >= 2)

    routines = segment(data, sorted(seeds))
    # rank by inbound refs
    ranked = []
    for r in routines:
        entry = int(r["entry"], 16)
        ranked.append({**r, "inbound_abs_refs": targets.get(entry, 0)})
    ranked.sort(key=lambda x: (-x["inbound_abs_refs"], x["entry"]))

    # Focus window around main init 0x075b
    init = [r for r in ranked if int(r["entry"], 16) <= 0x075B < int(r["end_exclusive"], 16)]
    near_init = [r for r in ranked if 0x0700 <= int(r["entry"], 16) <= 0x0900][:20]

    report = {
        "generated_at": now,
        "status": "scanned",
        "layer": "L3",
        "plan_ref": "BINARY_RE_PLAN.md",
        "path": str(RAM.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "source_note": "Volatile FX2 RAM — NOT eeprom.bin",
        "seed_entry_count": len(seeds),
        "routine_count": len(ranked),
        "all_routines": ranked,
        "top_routines_by_inbound": ranked[:40],
        "routine_covering_0x075b": init,
        "routines_near_init_0x0700_0x0900": near_init,
        "confidence": "hypothesis",
        "boundary": "RET-based segmentation is heuristic; overlapping/fall-through routines expected",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "next_layer": "L4 command dispatch candidates from opcode immediates + routine ownership",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "routines": report["routine_count"],
                "top": [{"entry": r["entry"], "refs": r["inbound_abs_refs"], "size": r["size_bytes"]} for r in ranked[:8]],
                "cover_075b": init,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
