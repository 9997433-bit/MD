#!/usr/bin/env python3
"""L4: map USB command opcodes to candidate handler regions in FX2 RAM.

Uses MOV A,#imm / CJNE A,#imm sites for opcodes seen on EP01, then attaches
owning L3 routine and nearby abs-call targets as handler candidates.
Cross-checks usb_cmd_data_correlation.json when present (oracle, not proof).

Writes manifests/fx2_cmd_dispatch_hypothesis.json.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
XREFS = ROOT / "manifests" / "fx2_ram_xrefs.json"
ROUTINES = ROOT / "manifests" / "fx2_ram_routines.json"
CORR = ROOT / "manifests" / "usb_cmd_data_correlation.json"
OUT = ROOT / "manifests" / "fx2_cmd_dispatch_hypothesis.json"

# High-frequency EP01 opcodes from session taxonomy / correlation.
FOCUS = ["0x01", "0x08", "0x09", "0x0a", "0x0b", "0x04", "0x05"]


def owning_routine(addr: int, routines: list[dict]) -> dict | None:
    for r in routines:
        a = int(r["entry"], 16)
        b = int(r["end_exclusive"], 16)
        if a <= addr < b:
            return {"entry": r["entry"], "end_exclusive": r["end_exclusive"], "inbound_abs_refs": r.get("inbound_abs_refs")}
    return None


def nearby_calls(data: bytes, center: int, window: int = 64) -> list[dict]:
    lo = max(0, center - window)
    hi = min(len(data) - 2, center + window)
    out = []
    for i in range(lo, hi + 1):
        if data[i] in (0x02, 0x12):
            dest = (data[i + 1] << 8) | data[i + 2]
            if dest < len(data):
                out.append({"at": f"0x{i:04x}", "op": "LJMP" if data[i] == 0x02 else "LCALL", "dest": f"0x{dest:04x}"})
    return out[:12]


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists() or not XREFS.exists():
        report = {"generated_at": now, "status": "missing", "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为"}
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    data = RAM.read_bytes()
    xrefs = json.loads(XREFS.read_text(encoding="utf-8"))
    routines = []
    if ROUTINES.exists():
        routines = json.loads(ROUTINES.read_text(encoding="utf-8")).get("top_routines_by_inbound") or []
        # Prefer full list if we stored only top — reload full file field
        full = json.loads(ROUTINES.read_text(encoding="utf-8"))
        # Rebuild from seeds by re-reading top + near — actually routines file only has top 40.
        # Use top 40 + recompute ownership via entries in top list is weak; re-run ownership from abs targets.
        routines = full.get("top_routines_by_inbound", [])

    # Expand routine list: recompute quick segments for ownership only
    from analyze_fx2_ram_routines import abs_targets, segment

    seeds = {0x0000}
    if data[0] == 0x02:
        seeds.add((data[1] << 8) | data[2])
    seeds.update(d for d, n in abs_targets(data).items() if n >= 2)
    all_routines = segment(data, sorted(seeds))
    for r in all_routines:
        r["inbound_abs_refs"] = abs_targets(data).get(int(r["entry"], 16), 0)

    sites = xrefs.get("cmd_opcode_imm_sites") or {}
    corr_top = {}
    if CORR.exists():
        c = json.loads(CORR.read_text(encoding="utf-8"))
        for row in c.get("opcodes_preceding_bursts_top") or []:
            corr_top[row["opcode"]] = row["burst_hits"]

    dispatch = []
    for op in FOCUS:
        addrs = sites.get(op) or []
        entries = []
        for ahex in addrs[:20]:
            addr = int(ahex, 16)
            owner = owning_routine(addr, all_routines)
            entries.append(
                {
                    "imm_site": ahex,
                    "owner_routine": owner,
                    "nearby_abs_branches": nearby_calls(data, addr),
                }
            )
        # Aggregate owner entries
        owner_counts: dict[str, int] = {}
        for e in entries:
            if e["owner_routine"]:
                k = e["owner_routine"]["entry"]
                owner_counts[k] = owner_counts.get(k, 0) + 1
        top_owners = sorted(owner_counts.items(), key=lambda x: -x[1])
        dispatch.append(
            {
                "opcode": op,
                "imm_site_count": len(addrs),
                "oracle_ep84_burst_precede_hits": corr_top.get(op),
                "dominant_owner_routines": [{"entry": k, "site_hits": v} for k, v in top_owners[:5]],
                "sites": entries[:10],
                "semantics": "unknown",
                "confidence": "hypothesis",
            }
        )

    report = {
        "generated_at": now,
        "status": "hypothesis",
        "layer": "L4",
        "plan_ref": "BINARY_RE_PLAN.md",
        "source_note": "Volatile FX2 RAM — NOT eeprom.bin; opcode meanings unconfirmed",
        "dispatch_candidates": dispatch,
        "priority_opcodes_for_ghidra": [
            {
                "opcode": "0x08",
                "why": "Highest EP84 burst-precede correlation in usb_cmd_data_correlation.json",
            },
            {
                "opcode": "0x01",
                "why": "Most frequent EP01 opcode in session taxonomy",
            },
            {
                "opcode": "0x09",
                "why": "Second-most frequent command-plane opcode",
            },
        ],
        "boundary": "Immediate matches ≠ dispatch proof; need Ghidra CFG confirmation",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "next_layer": "L5 datapath around EP6CFG/EP6CS/FIFORESET sites",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = [
        {
            "opcode": d["opcode"],
            "sites": d["imm_site_count"],
            "owners": d["dominant_owner_routines"][:3],
            "oracle": d["oracle_ep84_burst_precede_hits"],
        }
        for d in dispatch
    ]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
