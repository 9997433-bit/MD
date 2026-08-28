#!/usr/bin/env python3
"""L0/G0–G1: FX2 RAM address map + reset→init SFR access order (NOT eeprom.bin).

Writes:
  - manifests/fx2_address_map.json
  - manifests/fx2_init_chain.json
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
from disasm_8051_lite import disasm_region  # noqa: E402

RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
SCAN = ROOT / "manifests" / "fx2_ram_scan.json"
XREFS = ROOT / "manifests" / "fx2_ram_xrefs.json"
ROUTINES = ROOT / "manifests" / "fx2_ram_routines.json"
DISPATCH = ROOT / "manifests" / "fx2_cmd_dispatch_hypothesis.json"
DATAPATH = ROOT / "manifests" / "fx2_datapath_hypothesis.json"
IVT = ROOT / "manifests" / "fx2_ivt_map.json"
OUT_MAP = ROOT / "manifests" / "fx2_address_map.json"
OUT_INIT = ROOT / "manifests" / "fx2_init_chain.json"

SFR_LABELS = {
    0xE600: "CPUCS",
    0xE601: "IFCONFIG",
    0xE602: "PINFLAGSAB",
    0xE603: "PINFLAGSCD",
    0xE604: "FIFORESET",
    0xE610: "EP1OUTCFG",
    0xE611: "EP1INCFG",
    0xE612: "EP2CFG",
    0xE613: "EP4CFG",
    0xE614: "EP6CFG",
    0xE615: "EP8CFG",
    0xE618: "EP2FIFOCFG",
    0xE619: "EP4FIFOCFG",
    0xE61A: "EP6FIFOCFG",
    0xE61B: "EP8FIFOCFG",
    0xE65D: "OUTPKTEND",
    0xE65F: "INPKTEND",
    0xE678: "I2CS",
    0xE679: "I2DAT",
    0xE680: "USBCS",
    0xE68A: "EP4BCH",
    0xE68B: "EP4BCL",
    0xE68C: "EP6BCH",
    0xE68D: "EP6BCL",
    0xE68E: "EP8BCH",
    0xE68F: "EP8BCL",
    0xE6A0: "EP2CS",
    0xE6A1: "EP4CS",
    0xE6A2: "EP6CS",
    0xE6A3: "EP8CS",
    0xE6B3: "SUDPTRH",
    0xE6B4: "SUDPTRL",
    0xE6B5: "SUDPTRCTL",
    0xE6F5: "EP0BCH",
    0xE6F6: "EP0BCL",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def zero_runs(data: bytes, min_len: int = 32) -> list[dict]:
    runs = []
    i = 0
    n = len(data)
    while i < n:
        if data[i] != 0:
            i += 1
            continue
        j = i
        while j < n and data[j] == 0:
            j += 1
        if j - i >= min_len:
            runs.append({"start": f"0x{i:04x}", "end_exclusive": f"0x{j:04x}", "length": j - i})
        i = j
    return runs


def scan_abs_calls_in_range(data: bytes, start: int, end: int) -> list[dict]:
    hits = []
    end = min(end, len(data) - 2)
    i = start
    while i < end:
        op = data[i]
        if op in (0x02, 0x12) and i + 2 < len(data):
            dest = (data[i + 1] << 8) | data[i + 2]
            if dest < len(data):
                hits.append(
                    {
                        "at": f"0x{i:04x}",
                        "op": "LJMP" if op == 0x02 else "LCALL",
                        "dest": f"0x{dest:04x}",
                    }
                )
                i += 3
                continue
        i += 1
    return hits


def sfr_touches_in_routine(data: bytes, start: int, length: int = 0x180) -> list[dict]:
    """Disasm window; record DPTR loads to SFR and subsequent MOVX R/W."""
    insns = disasm_region(data, start, length, max_insns=220)
    dptr: int | None = None
    seq: list[dict] = []
    for row in insns:
        t = row["text"]
        if t.startswith("MOV DPTR,#0x"):
            dptr = int(t.split("#0x", 1)[1][:4], 16)
            label = SFR_LABELS.get(dptr)
            if 0xE600 <= dptr <= 0xE6FF:
                seq.append(
                    {
                        "at": row["addr"],
                        "op": "MOV_DPTR",
                        "imm": f"0x{dptr:04x}",
                        "label": label or f"E6xx_{dptr:04x}",
                    }
                )
            continue
        if t == "INC DPTR" and dptr is not None:
            dptr = (dptr + 1) & 0xFFFF
            continue
        if dptr is None or not (0xE600 <= dptr <= 0xE6FF):
            continue
        label = SFR_LABELS.get(dptr) or f"E6xx_{dptr:04x}"
        if t == "MOVX @DPTR,A":
            seq.append({"at": row["addr"], "op": "MOVX_WRITE", "imm": f"0x{dptr:04x}", "label": label})
        elif t == "MOVX A,@DPTR":
            seq.append({"at": row["addr"], "op": "MOVX_READ", "imm": f"0x{dptr:04x}", "label": label})
    return seq


def build_init_chain(data: bytes) -> dict:
    """G1: reset→CRT clear→main, then ordered early LCALL SFR touches (candidate)."""
    # Bytes at 0x0767: LJMP 0x07a5 (Keil-style after IRAM clear)
    post_crt = 0x07A5
    if data[0x0767:0x076A] == bytes([0x02, 0x07, 0xA5]):
        post_crt = 0x07A5

    early_calls = scan_abs_calls_in_range(data, post_crt, post_crt + 0x280)
    # Prefer LCALL order; keep first occurrence of each dest
    ordered_callees: list[dict] = []
    seen: set[int] = set()
    for c in early_calls:
        if c["op"] != "LCALL":
            continue
        dest = int(c["dest"], 16)
        if dest in seen:
            continue
        seen.add(dest)
        touches = sfr_touches_in_routine(data, dest)
        ordered_callees.append(
            {
                "call_at": c["at"],
                "entry": c["dest"],
                "sfr_touch_count": len(touches),
                "sfr_touches": touches[:40],
                "write_labels": [t["label"] for t in touches if t["op"] == "MOVX_WRITE"],
            }
        )

    # Flatten first-seen MOVX write labels across early callees (init-ish order)
    write_order: list[str] = []
    flat_writes: list[dict] = []
    for cal in ordered_callees:
        for t in cal["sfr_touches"]:
            if t["op"] != "MOVX_WRITE":
                continue
            flat_writes.append({**t, "via_callee": cal["entry"], "call_at": cal["call_at"]})
            if t["label"] not in write_order:
                write_order.append(t["label"])

    # Also annotate CRT prologue briefly
    crt = disasm_region(data, 0x075B, 0x20, max_insns=12)

    return {
        "reset_vector": "0x0000",
        "reset_target": "0x075b",
        "crt_prologue_preview": [r["text"] for r in crt],
        "crt_note": "0x075B clears IRAM then LJMP 0x07A5 (Keil-style runtime); SFR config is in callees",
        "post_crt_entry": f"0x{post_crt:04x}",
        "early_abs_calls": early_calls[:40],
        "early_callees_with_sfr": ordered_callees,
        "movx_write_label_first_seen_order": write_order,
        "movx_writes_flat": flat_writes[:60],
        "highlight_calls_to_0x1435": [c for c in early_calls if c.get("dest") == "0x1435"],
    }


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        stub = {"generated_at": now, "status": "missing", "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为"}
        OUT_MAP.write_text(json.dumps(stub, indent=2) + "\n")
        OUT_INIT.write_text(json.dumps(stub, indent=2) + "\n")
        print(json.dumps({"status": "missing"}))
        return

    data = RAM.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    scan = load_json(SCAN)
    xrefs = load_json(XREFS)
    routines = load_json(ROUTINES)
    dispatch = load_json(DISPATCH)
    datapath = load_json(DATAPATH)
    ivt = load_json(IVT)

    anchors = [
        {"name": "image_base", "start": "0x0000", "end_exclusive": f"0x{len(data):04x}", "role": "volatile_code_xdata_image"},
        {"name": "reset_vector", "start": "0x0000", "role": "ivt_reset", "ljmp": "0x075b"},
        {"name": "main_init", "start": "0x075b", "role": "reset_target"},
        {"name": "hot_abs_0x0393", "start": "0x0393", "role": "abs_branch_hotspot"},
        {"name": "cmd_0x01_owner_candidate", "start": "0x0473", "role": "ep1_opcode_imm_owner"},
        {"name": "cmd_0x08_datapath_hub", "start": "0x1435", "role": "ep1_opcode_and_fifo_hub"},
    ]
    # Enrich from dispatch / datapath if present
    for cand in (dispatch.get("dispatch_candidates") or [])[:6]:
        owners = cand.get("dominant_owner_routines") or []
        if owners:
            anchors.append(
                {
                    "name": f"opcode_{cand['opcode']}_owner",
                    "start": owners[0]["entry"],
                    "role": "ep1_dispatch_owner_candidate",
                    "opcode": cand["opcode"],
                }
            )
    for r in (datapath.get("datapath_routine_candidates") or [])[:5]:
        anchors.append(
            {
                "name": f"datapath_{r.get('entry')}",
                "start": r.get("entry"),
                "role": "fifo_ep_in_candidate",
                "score": r.get("score"),
            }
        )

    regions = {
        "code_image": {"start": "0x0000", "end_exclusive": f"0x{len(data):04x}", "note": "FX2 on-chip code/xdata RAM loaded via 0xA0"},
        "ivt_classic": {"start": "0x0000", "end_exclusive": "0x0046", "note": "classic 8051 vectors + USB hint slot"},
        "sfr_xdata_window": {
            "start": "0xe600",
            "end_exclusive": "0xe700",
            "note": "FX2 SFR/XDATA; not inside RAM image bytes — referenced via MOV DPTR",
            "in_image": False,
        },
        "zero_runs_ge_32": zero_runs(data),
    }

    addr_map = {
        "generated_at": now,
        "status": "mapped",
        "layer": "G0-G1",
        "plan_ref": "BINARY_RE_PLAN.md",
        "path": str(RAM.relative_to(ROOT)),
        "size_bytes": len(data),
        "sha256": sha,
        "source_note": "Volatile FX2 RAM from USB 0xA0 — NOT eeprom.bin; map is code anchors + SFR refs, not full physical XRAM census",
        "regions": regions,
        "ivt": ivt.get("vectors") or xrefs.get("vectors") or [],
        "anchors": anchors,
        "sfr_label_coverage": xrefs.get("sfr_label_coverage") or [],
        "reset": scan.get("reset_vector_hint") or {"bytes": "02075b", "target": "0x075b"},
        "routine_seed_count": routines.get("routine_count"),
        "confidence": "candidate",
        "boundary": "candidate map from RAM image only; EEPROM dump may extend/alter layout",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT_MAP.write_text(json.dumps(addr_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    chain = build_init_chain(data)
    init = {
        "generated_at": now,
        "status": "scanned",
        "layer": "G1",
        "plan_ref": "BINARY_RE_PLAN.md",
        "source_note": "Reset→CRT→early LCALL SFR walk on fx2_ram_from_enum.bin — NOT eeprom.bin; not a full CFG",
        **chain,
        "interpretation": (
            "After IRAM clear, early LCALL targets are scanned for MOV DPTR,#E6xx + MOVX; "
            "first-seen write labels form an init/config candidate order. "
            "Early transfer to 0x1435 links init to the EP6/FIFO hub candidate."
        ),
        "confidence": "candidate",
        "boundary": "byte-scan LCALL + lite disasm of callees; misaligned false positives possible",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT_INIT.write_text(json.dumps(init, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "sha256": sha,
                "anchors": len(anchors),
                "zero_runs": len(regions["zero_runs_ge_32"]),
                "early_callees": len(chain["early_callees_with_sfr"]),
                "write_label_order": chain["movx_write_label_first_seen_order"],
                "calls_to_1435": chain["highlight_calls_to_0x1435"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
