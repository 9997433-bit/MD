#!/usr/bin/env python3
"""L6: cross-check binary dispatch/datapath candidates against USB session oracle.

Writes manifests/fx2_oracle_crosscheck.json.
Raises confidence to candidate only when BOTH binary owner and EP84-precede agree.
Never claims confirmed opcode semantics.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPATCH = ROOT / "manifests" / "fx2_cmd_dispatch_hypothesis.json"
DATAPATH = ROOT / "manifests" / "fx2_datapath_hypothesis.json"
CORR = ROOT / "manifests" / "usb_cmd_data_correlation.json"
TAX = ROOT / "manifests" / "usb_command_taxonomy.json"
OUT = ROOT / "manifests" / "fx2_oracle_crosscheck.json"


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    missing = [str(p.relative_to(ROOT)) for p in (DISPATCH, DATAPATH, CORR) if not p.exists()]
    if missing:
        report = {
            "generated_at": now,
            "status": "missing",
            "missing": missing,
            "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        }
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    disp = json.loads(DISPATCH.read_text(encoding="utf-8"))
    data = json.loads(DATAPATH.read_text(encoding="utf-8"))
    corr = json.loads(CORR.read_text(encoding="utf-8"))

    precede = {r["opcode"]: r["burst_hits"] for r in corr.get("opcodes_preceding_bursts_top") or []}
    top_dp = (data.get("datapath_routine_candidates") or [{}])[0].get("entry")
    dp_labels = (data.get("datapath_routine_candidates") or [{}])[0].get("labels")

    findings = []
    for d in disp.get("dispatch_candidates") or []:
        op = d["opcode"]
        owners = d.get("dominant_owner_routines") or []
        owner = owners[0]["entry"] if owners else None
        oracle_hits = precede.get(op) or d.get("oracle_ep84_burst_precede_hits")
        overlap = owner is not None and top_dp is not None and owner == top_dp
        conf = "hypothesis"
        note = "insufficient joint evidence"
        if owner and oracle_hits and oracle_hits >= 50:
            conf = "candidate"
            note = "binary owner + strong EP84-precede oracle"
        if overlap and oracle_hits:
            conf = "candidate"
            note = "owner equals top datapath routine AND EP84-precede oracle"
        findings.append(
            {
                "opcode": op,
                "binary_owner_routine": owner,
                "oracle_ep84_precede_hits": oracle_hits,
                "overlaps_top_datapath_routine": overlap,
                "top_datapath_routine": top_dp,
                "confidence": conf,
                "note": note,
                "semantics": "unknown",
            }
        )

    # Highlight 0x08 specially
    star = next((f for f in findings if f["opcode"] == "0x08"), None)

    report = {
        "generated_at": now,
        "status": "crosschecked",
        "layer": "L6",
        "plan_ref": "BINARY_RE_PLAN.md",
        "source_note": "Binary from fx2_ram_from_enum.bin; oracle from usb_session — NOT eeprom.bin",
        "top_datapath_routine": top_dp,
        "top_datapath_labels": dp_labels,
        "findings": findings,
        "headline": star,
        "taxonomy_opcode_count": len((json.loads(TAX.read_text()) if TAX.exists() else {}).get("out_opcodes") or []),
        "boundary": "candidate ≠ confirmed semantics; still need Ghidra CFG + controlled experiments",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "headline": report["headline"],
                "candidate_opcodes": [f["opcode"] for f in findings if f["confidence"] == "candidate"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
