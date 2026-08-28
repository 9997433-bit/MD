#!/usr/bin/env python3
"""L5: FIFO / EP6 datapath candidate sites in FX2 RAM image.

Clusters MOV DPTR,#imm hits for EP6/EP4/FIFO/IFCONFIG related SFR labels
and reports routine ownership + proximity. Writes manifests/fx2_datapath_hypothesis.json.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
XREFS = ROOT / "manifests" / "fx2_ram_xrefs.json"
OUT = ROOT / "manifests" / "fx2_datapath_hypothesis.json"

DATA_LABELS = {
    "EP6CFG",
    "EP6CS",
    "EP4CFG",
    "EP4CS",
    "EP2CS",
    "FIFORESET",
    "IFCONFIG",
    "PINFLAGSAB",
    "EP1OUTCFG",
    "EP1INCFG",
}


def owning(addr: int, segments: list[tuple[int, int, str]]) -> str | None:
    for a, b, e in segments:
        if a <= addr < b:
            return e
    return None


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists() or not XREFS.exists():
        report = {"generated_at": now, "status": "missing", "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为"}
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    data = RAM.read_bytes()
    xrefs = json.loads(XREFS.read_text(encoding="utf-8"))

    from analyze_fx2_ram_routines import abs_targets, segment

    seeds = {0x0000}
    if data[0] == 0x02:
        seeds.add((data[1] << 8) | data[2])
    seeds.update(d for d, n in abs_targets(data).items() if n >= 2)
    segs = []
    for r in segment(data, sorted(seeds)):
        segs.append((int(r["entry"], 16), int(r["end_exclusive"], 16), r["entry"]))

    by_label: dict[str, list[dict]] = defaultdict(list)
    for hit in xrefs.get("sfr_dptr_hits") or []:
        lab = hit.get("label")
        if lab not in DATA_LABELS:
            continue
        addr = int(hit["at"], 16)
        by_label[lab].append(
            {
                "at": hit["at"],
                "imm": hit["imm"],
                "owner_routine": owning(addr, segs),
            }
        )

    # Cluster: routines that touch EP6* + FIFORESET are strong datapath candidates
    routine_score: dict[str, dict] = {}
    for lab, hits in by_label.items():
        for h in hits:
            e = h["owner_routine"] or "unknown"
            slot = routine_score.setdefault(e, {"entry": e, "labels": set(), "hit_count": 0})
            slot["labels"].add(lab)
            slot["hit_count"] += 1

    ranked = []
    for e, s in routine_score.items():
        labels = sorted(s["labels"])
        score = s["hit_count"] + (5 if "EP6CFG" in labels or "EP6CS" in labels else 0)
        score += 3 if "FIFORESET" in labels else 0
        ranked.append({"entry": e, "labels": labels, "hit_count": s["hit_count"], "score": score})
    ranked.sort(key=lambda x: (-x["score"], x["entry"]))

    report = {
        "generated_at": now,
        "status": "hypothesis",
        "layer": "L5",
        "plan_ref": "BINARY_RE_PLAN.md",
        "source_note": "Volatile FX2 RAM — NOT eeprom.bin",
        "usb_data_plane_note": "Host session uses bulk EP 0x06/0x84; FX2 side often maps EP6/EP8 — labels are public TRM names, board mapping candidate only",
        "sfr_sites_by_label": {k: v for k, v in sorted(by_label.items())},
        "datapath_routine_candidates": ranked[:25],
        "primary_followups_for_ghidra": [r["entry"] for r in ranked[:8] if r["entry"] != "unknown"],
        "packing_link": "manifests/usb_sample_packing_hypothesis.json",
        "confidence": "hypothesis",
        "boundary": "SFR DPTR immediates suggest access sites, not proven sample packing logic",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "next_layer": "L6 deepen oracle; L4/L5 Ghidra CFG; L7 eeprom when available",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "labels": list(by_label.keys()),
                "top_routines": ranked[:8],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
