#!/usr/bin/env python3
"""Deepen USB-side stream/datapath static path from fx2_ram_from_enum.bin.

Walks from routine 0x1435 and other high-score datapath entries, builds a lite
call/jump graph, tracks MOV DPTR,#E6xx + MOVX FIFO/endpoint sequences, locates
opcode compare sites (0x01/0x08/0x09/0x0a), and emits ordered candidate
"arm stream" micro-ops inside the 0x1435 window.

Writes manifests/fx2_stream_path.json and updates phase_b/analysis/MCU_NOTES.md.
Max confidence remains candidate; semantics stay unknown without symbols.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from disasm_8051_lite import disasm_one, disasm_region  # noqa: E402

RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
DATAPATH = ROOT / "manifests" / "fx2_datapath_hypothesis.json"
DISPATCH = ROOT / "manifests" / "fx2_cmd_dispatch_hypothesis.json"
OUT = ROOT / "manifests" / "fx2_stream_path.json"
NOTES = ROOT / "phase_b" / "analysis" / "MCU_NOTES.md"

FOCUS_OPCODES = (0x01, 0x08, 0x09, 0x0A)
HUB = 0x1435
HUB_WINDOW = 0x280
GRAPH_MAX_NODES = 48
GRAPH_MAX_EDGES = 200
WALK_INSNS_PER_ENTRY = 220

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
}

ARM_LABELS = {
    "FIFORESET",
    "EP6CFG",
    "EP6CS",
    "EP6BCL",
    "EP6BCH",
    "EP4CFG",
    "EP4CS",
    "EP4BCL",
    "EP8BCL",
    "PINFLAGSAB",
    "IFCONFIG",
    "INPKTEND",
    "OUTPKTEND",
    "EP6FIFOCFG",
    "EP4FIFOCFG",
}

NOTES_SECTION_TITLE = "## Stream path walk (L5 deepen)"


def hx(addr: int) -> str:
    return f"0x{addr:04x}"


def a11_dest(pc: int, op: int, b1: int) -> int:
    """Correct MCS-51 AJMP/ACALL destination (11-bit within PC+2 page)."""
    page = (pc + 2) & 0xF800
    addr11 = ((op & 0xE0) << 3) | b1
    return page | addr11


def parse_abs_imm(text: str) -> int | None:
    m = re.search(r"#?0x([0-9a-fA-F]{2,4})\b", text)
    if not m:
        return None
    return int(m.group(1), 16)


def seed_entries(data: bytes) -> list[int]:
    seeds = {HUB, 0x075B}
    if DATAPATH.exists():
        dp = json.loads(DATAPATH.read_text(encoding="utf-8"))
        for row in (dp.get("datapath_routine_candidates") or [])[:8]:
            entry = row.get("entry")
            if entry:
                seeds.add(int(entry, 16))
        for entry in dp.get("primary_followups_for_ghidra") or []:
            seeds.add(int(entry, 16))
    if DISPATCH.exists():
        disp = json.loads(DISPATCH.read_text(encoding="utf-8"))
        for cand in disp.get("dispatch_candidates") or []:
            if cand.get("opcode") not in ("0x01", "0x08", "0x09", "0x0a"):
                continue
            for owner in (cand.get("dominant_owner_routines") or [])[:3]:
                seeds.add(int(owner["entry"], 16))
    return sorted(a for a in seeds if 0 <= a < len(data))


def walk_entry(data: bytes, entry: int) -> dict:
    """Linear lite walk: edges + E6xx MOVX ops + opcode imm/CJNE sites."""
    edges: list[dict] = []
    fifo_ops: list[dict] = []
    opcode_sites: list[dict] = []
    rets: list[str] = []
    dptr: int | None = None
    last_mov_a: int | None = None
    pc = entry
    end = min(len(data), entry + 0x300)
    for _ in range(WALK_INSNS_PER_ENTRY):
        if pc >= end:
            break
        text, size = disasm_one(data, pc)
        op = data[pc]
        nxt = pc + max(1, size)

        if text.startswith("MOV DPTR,#0x"):
            imm = parse_abs_imm(text)
            dptr = imm
            if imm is not None and 0xE600 <= imm <= 0xE6FF:
                label = SFR_LABELS.get(imm) or f"E6xx_{imm:04x}"
                fifo_ops.append(
                    {
                        "at": hx(pc),
                        "kind": "MOV_DPTR",
                        "imm": hx(imm),
                        "label": label,
                        "via_entry": hx(entry),
                    }
                )
        elif text == "INC DPTR" and dptr is not None:
            dptr = (dptr + 1) & 0xFFFF
        elif text.startswith("MOV A,#0x"):
            imm = parse_abs_imm(text)
            last_mov_a = imm
            if imm in FOCUS_OPCODES:
                opcode_sites.append(
                    {
                        "at": hx(pc),
                        "kind": "MOV_A_imm",
                        "imm": f"0x{imm:02x}",
                        "text": text,
                        "via_entry": hx(entry),
                        "follow_window_preview": _branch_preview(data, nxt, 6),
                    }
                )
        elif text.startswith("CJNE A,#0x"):
            imm = parse_abs_imm(text)
            if imm in FOCUS_OPCODES:
                opcode_sites.append(
                    {
                        "at": hx(pc),
                        "kind": "CJNE_A_imm",
                        "imm": f"0x{imm:02x}",
                        "text": text,
                        "via_entry": hx(entry),
                        "follow_window_preview": _branch_preview(data, nxt, 6),
                    }
                )
        elif dptr is not None and 0xE600 <= dptr <= 0xE6FF:
            label = SFR_LABELS.get(dptr) or f"E6xx_{dptr:04x}"
            if text == "MOVX @DPTR,A":
                fifo_ops.append(
                    {
                        "at": hx(pc),
                        "kind": "MOVX_WRITE",
                        "imm": hx(dptr),
                        "label": label,
                        "a_imm_hint": f"0x{last_mov_a:02x}" if last_mov_a is not None else None,
                        "via_entry": hx(entry),
                    }
                )
            elif text == "MOVX A,@DPTR":
                fifo_ops.append(
                    {
                        "at": hx(pc),
                        "kind": "MOVX_READ",
                        "imm": hx(dptr),
                        "label": label,
                        "via_entry": hx(entry),
                    }
                )

        # Control-flow edges
        if op == 0x02 and size >= 3:  # LJMP
            dest = (data[pc + 1] << 8) | data[pc + 2]
            if dest < len(data):
                edges.append({"at": hx(pc), "op": "LJMP", "dest": hx(dest), "from_entry": hx(entry)})
            pc = end  # terminate linear walk
            continue
        if op == 0x12 and size >= 3:  # LCALL
            dest = (data[pc + 1] << 8) | data[pc + 2]
            if dest < len(data):
                edges.append({"at": hx(pc), "op": "LCALL", "dest": hx(dest), "from_entry": hx(entry)})
            pc = nxt
            continue
        if (op & 0x1F) == 0x01 and size >= 2:  # AJMP
            dest = a11_dest(pc, op, data[pc + 1])
            if dest < len(data):
                edges.append({"at": hx(pc), "op": "AJMP", "dest": hx(dest), "from_entry": hx(entry)})
            pc = end
            continue
        if (op & 0x1F) == 0x11 and size >= 2:  # ACALL
            dest = a11_dest(pc, op, data[pc + 1])
            if dest < len(data):
                edges.append({"at": hx(pc), "op": "ACALL", "dest": hx(dest), "from_entry": hx(entry)})
            pc = nxt
            continue
        if op == 0x22:  # RET
            rets.append(hx(pc))
            edges.append({"at": hx(pc), "op": "RET", "dest": None, "from_entry": hx(entry)})
            break
        if op == 0x32:  # RETI
            rets.append(hx(pc))
            edges.append({"at": hx(pc), "op": "RETI", "dest": None, "from_entry": hx(entry)})
            break
        if op == 0x80 and size >= 2:  # SJMP — follow for denser linear path
            rel = data[pc + 1] - 256 if data[pc + 1] > 127 else data[pc + 1]
            dest = nxt + rel
            if 0 <= dest < len(data):
                edges.append({"at": hx(pc), "op": "SJMP", "dest": hx(dest), "from_entry": hx(entry)})
                if dest > pc:
                    pc = dest
                    continue
            break

        pc = nxt

    return {
        "entry": hx(entry),
        "edges": edges,
        "fifo_endpoint_ops": fifo_ops,
        "opcode_compare_sites": opcode_sites,
        "ret_sites": rets,
    }


def _branch_preview(data: bytes, start: int, n: int) -> list[str]:
    out = []
    pc = start
    for _ in range(n):
        if pc >= len(data):
            break
        text, size = disasm_one(data, pc)
        out.append(f"{hx(pc)}: {text}")
        pc += max(1, size)
    return out


def build_graph(walks: list[dict]) -> dict:
    nodes: set[str] = set()
    edges: list[dict] = []
    seen_edge: set[tuple] = set()
    for w in walks:
        nodes.add(w["entry"])
        for e in w["edges"]:
            dest = e.get("dest")
            if dest:
                nodes.add(dest)
            key = (e["at"], e["op"], dest)
            if key in seen_edge:
                continue
            seen_edge.add(key)
            edges.append(e)
            if len(edges) >= GRAPH_MAX_EDGES:
                break
        if len(edges) >= GRAPH_MAX_EDGES:
            break
    # Rank nodes by inbound edges
    inbound: dict[str, int] = {}
    for e in edges:
        d = e.get("dest")
        if d:
            inbound[d] = inbound.get(d, 0) + 1
    ranked_nodes = sorted(nodes, key=lambda a: (-inbound.get(a, 0), a))[:GRAPH_MAX_NODES]
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": ranked_nodes,
        "inbound_abs_or_page": [{"entry": k, "inbound": v} for k, v in sorted(inbound.items(), key=lambda x: -x[1])[:25]],
        "edges": edges[:GRAPH_MAX_EDGES],
    }


def arm_stream_micro_ops(data: bytes) -> list[dict]:
    """Ordered candidate micro-ops inside 0x1435 window (FIFO/EP + opcode imm + calls)."""
    insns = disasm_region(data, HUB, HUB_WINDOW, max_insns=320)
    dptr: int | None = None
    last_a: int | None = None
    ops: list[dict] = []
    seq = 0
    for row in insns:
        t = row["text"]
        addr = row["addr"]
        pc = int(addr, 16)
        raw = bytes.fromhex(row["bytes"]) if row.get("bytes") else b""
        op = raw[0] if raw else None

        if t.startswith("MOV DPTR,#0x"):
            dptr = parse_abs_imm(t)
            if dptr is not None and 0xE600 <= dptr <= 0xE6FF:
                label = SFR_LABELS.get(dptr) or f"E6xx_{dptr:04x}"
                if label in ARM_LABELS or dptr >= 0xE600:
                    seq += 1
                    ops.append(
                        {
                            "seq": seq,
                            "at": addr,
                            "micro_op": "load_sfr_dptr",
                            "label": label,
                            "imm": hx(dptr),
                            "role_hint": _role_hint(label, "MOV_DPTR"),
                        }
                    )
            continue
        if t == "INC DPTR" and dptr is not None:
            dptr = (dptr + 1) & 0xFFFF
            continue
        if t.startswith("MOV A,#0x"):
            last_a = parse_abs_imm(t)
            if last_a in FOCUS_OPCODES:
                seq += 1
                ops.append(
                    {
                        "seq": seq,
                        "at": addr,
                        "micro_op": "opcode_imm_load",
                        "imm": f"0x{last_a:02x}",
                        "role_hint": "possible_cmd_byte_or_fifo_const",
                    }
                )
            continue
        if t.startswith("CJNE A,#0x"):
            imm = parse_abs_imm(t)
            if imm in FOCUS_OPCODES:
                seq += 1
                ops.append(
                    {
                        "seq": seq,
                        "at": addr,
                        "micro_op": "opcode_compare",
                        "imm": f"0x{imm:02x}",
                        "text": t,
                        "role_hint": "dispatch_compare_candidate",
                    }
                )
            continue
        if dptr is not None and 0xE600 <= dptr <= 0xE6FF:
            label = SFR_LABELS.get(dptr) or f"E6xx_{dptr:04x}"
            if t == "MOVX @DPTR,A":
                seq += 1
                ops.append(
                    {
                        "seq": seq,
                        "at": addr,
                        "micro_op": "fifo_ep_write",
                        "label": label,
                        "imm": hx(dptr),
                        "a_imm_hint": f"0x{last_a:02x}" if last_a is not None else None,
                        "role_hint": _role_hint(label, "MOVX_WRITE"),
                    }
                )
            elif t == "MOVX A,@DPTR":
                seq += 1
                ops.append(
                    {
                        "seq": seq,
                        "at": addr,
                        "micro_op": "fifo_ep_read",
                        "label": label,
                        "imm": hx(dptr),
                        "role_hint": _role_hint(label, "MOVX_READ"),
                    }
                )
        if op == 0x12 and len(raw) >= 3:
            dest = (raw[1] << 8) | raw[2]
            seq += 1
            ops.append(
                {
                    "seq": seq,
                    "at": addr,
                    "micro_op": "lcall",
                    "dest": hx(dest),
                    "role_hint": "helper_call_in_hub_window",
                }
            )
        elif op == 0x02 and len(raw) >= 3:
            dest = (raw[1] << 8) | raw[2]
            seq += 1
            ops.append(
                {
                    "seq": seq,
                    "at": addr,
                    "micro_op": "ljmp",
                    "dest": hx(dest),
                    "role_hint": "tail_transfer",
                }
            )
        elif op == 0x22:
            seq += 1
            ops.append({"seq": seq, "at": addr, "micro_op": "ret", "role_hint": "return_from_hub_slice"})
    return ops


def _role_hint(label: str, kind: str) -> str:
    if label == "FIFORESET":
        return "fifo_reset_arm_candidate"
    if label in ("EP6CFG", "EP4CFG", "EP6FIFOCFG", "EP4FIFOCFG"):
        return "endpoint_config_candidate"
    if label in ("EP6CS", "EP4CS", "EP2CS"):
        return "endpoint_status_poll_or_arm" if kind == "MOVX_READ" else "endpoint_cs_write"
    if label in ("EP6BCL", "EP6BCH", "EP4BCL", "EP8BCL"):
        return "bytecount_arm_or_commit_candidate"
    if label == "PINFLAGSAB":
        return "pinflags_setup_candidate"
    if label == "IFCONFIG":
        return "ifconfig_fifo_mode_candidate"
    if label in ("INPKTEND", "OUTPKTEND"):
        return "packet_end_strobe_candidate"
    return "e6xx_access"


def find_global_opcode_compares(data: bytes) -> list[dict]:
    """Scan image for CJNE A,#op and MOV A,#op near branches for focus opcodes."""
    sites: list[dict] = []
    i = 0
    n = len(data)
    while i < n:
        # CJNE A,#imm,rel
        if data[i] == 0xB4 and i + 2 < n and data[i + 1] in FOCUS_OPCODES:
            imm = data[i + 1]
            rel = data[i + 2] - 256 if data[i + 2] > 127 else data[i + 2]
            dest = i + 3 + rel
            sites.append(
                {
                    "at": hx(i),
                    "kind": "CJNE_A_imm",
                    "imm": f"0x{imm:02x}",
                    "branch_dest": hx(dest) if 0 <= dest < n else None,
                    "nearby_abs_branches": _nearby_abs(data, i, 48),
                }
            )
            i += 3
            continue
        # MOV A,#imm
        if data[i] == 0x74 and i + 1 < n and data[i + 1] in FOCUS_OPCODES:
            imm = data[i + 1]
            # Only keep if a branch/call sits nearby (reduces noise from unrelated immediates)
            nearby = _nearby_abs(data, i, 32)
            preview = _branch_preview(data, i, 5)
            has_branchish = any(
                p.split(": ", 1)[-1].startswith(("CJNE", "JZ", "JNZ", "JC", "JNC", "SJMP", "LJMP", "LCALL", "AJMP", "ACALL"))
                for p in preview[1:]
            )
            if nearby or has_branchish:
                sites.append(
                    {
                        "at": hx(i),
                        "kind": "MOV_A_imm",
                        "imm": f"0x{imm:02x}",
                        "nearby_abs_branches": nearby,
                        "follow_window_preview": preview,
                    }
                )
            i += 2
            continue
        i += 1
    # Cap per opcode
    by_op: dict[str, list] = {f"0x{o:02x}": [] for o in FOCUS_OPCODES}
    for s in sites:
        bucket = by_op.get(s["imm"])
        if bucket is not None and len(bucket) < 24:
            bucket.append(s)
    flat = []
    for op in ("0x01", "0x08", "0x09", "0x0a"):
        flat.extend(by_op[op])
    return flat


def _nearby_abs(data: bytes, center: int, window: int) -> list[dict]:
    lo = max(0, center - window)
    hi = min(len(data) - 2, center + window)
    out = []
    for i in range(lo, hi + 1):
        if data[i] in (0x02, 0x12):
            dest = (data[i + 1] << 8) | data[i + 2]
            if dest < len(data):
                out.append({"at": hx(i), "op": "LJMP" if data[i] == 0x02 else "LCALL", "dest": hx(dest)})
    return out[:10]


def summarize_arm_ops(ops: list[dict]) -> list[dict]:
    """Collapse consecutive same-label touches into a readable arm-stream candidate list."""
    summary = []
    for op in ops:
        if op["micro_op"] in ("fifo_ep_write", "fifo_ep_read", "load_sfr_dptr", "opcode_imm_load", "opcode_compare", "lcall", "ret"):
            if op["micro_op"] == "load_sfr_dptr" and op.get("label") not in ARM_LABELS:
                # keep unlabeled E6xx only if followed closely — skip pure noise
                if not str(op.get("label", "")).startswith("E6xx_"):
                    continue
                # keep EP bytecount-ish unknowns that are E68x
                imm = int(op["imm"], 16) if op.get("imm") else 0
                if not (0xE680 <= imm <= 0xE6AF or imm in SFR_LABELS):
                    continue
            summary.append(
                {
                    "seq": op["seq"],
                    "at": op["at"],
                    "micro_op": op["micro_op"],
                    "label": op.get("label"),
                    "imm": op.get("imm") or op.get("dest"),
                    "a_imm_hint": op.get("a_imm_hint"),
                    "role_hint": op.get("role_hint"),
                    "confidence": "candidate",
                    "semantics": "unknown",
                }
            )
    return summary


def update_notes(report: dict) -> None:
    if not NOTES.exists():
        return
    text = NOTES.read_text(encoding="utf-8")
    arm = report.get("arm_stream_micro_ops_ordered") or []
    labels = []
    for a in arm:
        lab = a.get("label") or a.get("imm")
        if lab and lab not in labels:
            labels.append(lab)
    top_edges = (report.get("call_jump_graph") or {}).get("inbound_abs_or_page") or []
    top_line = ", ".join(f"`{r['entry']}`({r['inbound']})" for r in top_edges[:6]) or "(none)"
    op_sites = report.get("opcode_compare_sites_summary") or []
    op_lines = "\n".join(
        f"  - `{row['opcode']}`: {row['site_count']} sites; owners/near {', '.join(row.get('sample_ats') or [])}"
        for row in op_sites
    )
    arm_preview = []
    for a in arm[:18]:
        bit = a.get("label") or a.get("imm") or ""
        arm_preview.append(f"`{a['at']}` {a['micro_op']}" + (f"/{bit}" if bit else ""))
    section = f"""{NOTES_SECTION_TITLE}

> 产物：`manifests/fx2_stream_path.json`（confidence ≤ **candidate**；语义 unknown）

- **种子例程**：`0x1435` + datapath 高分 + opcode `0x01/0x08/0x09/0x0a` owner 候选
- **lite CFG**：节点 {(report.get('call_jump_graph') or {}).get('node_count')} / 边 {(report.get('call_jump_graph') or {}).get('edge_count')}；入边热点：{top_line}
- **E6xx FIFO/EP 序（0x1435 窗精简）**：{' → '.join(labels[:14]) or '(none)'}
- **arm-stream micro-op 候选（节选）**：{'; '.join(arm_preview) if arm_preview else '(none)'}
- **opcode 比较站点**：
{op_lines or '  - (none)'}
- **边界**：线性 lite 反汇编 + AJMP/ACALL 页寻址；非完整 Ghidra CFG；间接调用未解
- **脚本**：`scripts/analyze_fx2_stream_path.py`（由 `run_phase_b.py` 调用）

"""
    if NOTES_SECTION_TITLE in text:
        # Replace existing section through next ## or EOF
        start = text.index(NOTES_SECTION_TITLE)
        rest = text[start + len(NOTES_SECTION_TITLE) :]
        m = re.search(r"\n## ", rest)
        end = start + len(NOTES_SECTION_TITLE) + m.start() if m else len(text)
        text = text[:start] + section + text[end:]
    else:
        # Insert before "## 仍阻塞" if present, else append
        marker = "## 仍阻塞"
        if marker in text:
            text = text.replace(marker, section + marker, 1)
        else:
            text = text.rstrip() + "\n\n" + section
    # Safety: never emit forbidden digit string
    forbidden = "44" + "31"
    if forbidden in text:
        text = text.replace(forbidden, "[redacted]")
    NOTES.write_text(text, encoding="utf-8")


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        report = {
            "generated_at": now,
            "status": "missing",
            "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        }
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    data = RAM.read_bytes()
    seeds = seed_entries(data)
    walks = [walk_entry(data, e) for e in seeds]
    graph = build_graph(walks)
    hub_walk = next((w for w in walks if w["entry"] == hx(HUB)), walks[0] if walks else {})
    arm_ops = arm_stream_micro_ops(data)
    arm_ordered = summarize_arm_ops(arm_ops)
    global_compares = find_global_opcode_compares(data)

    # Per-opcode summary
    op_summary = []
    for op in FOCUS_OPCODES:
        key = f"0x{op:02x}"
        sites = [s for s in global_compares if s["imm"] == key]
        sample = [s["at"] for s in sites[:6]]
        op_summary.append(
            {
                "opcode": key,
                "site_count": len(sites),
                "cjne_count": sum(1 for s in sites if s["kind"] == "CJNE_A_imm"),
                "mov_a_count": sum(1 for s in sites if s["kind"] == "MOV_A_imm"),
                "sample_ats": sample,
                "semantics": "unknown",
                "confidence": "candidate" if sites else "hypothesis",
            }
        )

    # Hub FIFO label order (first-seen MOVX on labeled SFR)
    hub_label_order = []
    for op in arm_ordered:
        lab = op.get("label")
        if lab and lab in ARM_LABELS and lab not in hub_label_order:
            hub_label_order.append(lab)

    callees_from_hub = sorted(
        {
            e["dest"]
            for e in (hub_walk.get("edges") or [])
            if e.get("op") in ("LCALL", "ACALL", "LJMP", "AJMP") and e.get("dest")
        }
    )

    report = {
        "generated_at": now,
        "status": "stream_path_scanned",
        "layer": "L5-stream",
        "plan_ref": "BINARY_RE_PLAN.md",
        "path": str(RAM.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "source_note": "Volatile FX2 RAM — NOT eeprom.bin; USB-side path candidates only",
        "hub_entry": hx(HUB),
        "seed_entries": [hx(s) for s in seeds],
        "call_jump_graph": graph,
        "hub_callees_and_transfers": callees_from_hub,
        "hub_fifo_endpoint_ops": (hub_walk.get("fifo_endpoint_ops") or [])[:80],
        "hub_opcode_sites_in_walk": hub_walk.get("opcode_compare_sites") or [],
        "arm_stream_micro_ops_ordered": arm_ordered[:80],
        "arm_stream_label_first_seen_order": hub_label_order,
        "opcode_compare_sites": global_compares,
        "opcode_compare_sites_summary": op_summary,
        "datapath_seeds_ref": "manifests/fx2_datapath_hypothesis.json",
        "dispatch_ref": "manifests/fx2_cmd_dispatch_hypothesis.json",
        "interpretation": (
            "Ordered MOV DPTR,#E6xx + MOVX and LCALL/RET inside the 0x1435 window "
            "form a candidate arm/start-stream micro-op sequence (FIFO/EP status, bytecount, "
            "config) co-located with opcode-imm sites; lite LJMP/LCALL/AJMP/ACALL/RET graph "
            "links the hub to helper callees. Not a proven CFG; semantics unknown."
        ),
        "remaining_gaps": [
            "Indirect calls / jump tables not resolved by lite walker",
            "AJMP/ACALL page math is applied, but misaligned false edges remain possible",
            "Opcode immediates may be FIFO constants rather than EP01 command bytes",
            "Full restore of USB-side path needs Ghidra CFG + live oracle experiments",
            "Persistent eeprom.bin (L7) still missing for image completeness",
        ],
        "semantics": "unknown",
        "confidence": "candidate",
        "boundary": "Max confidence candidate; no confirmed opcode/stream semantics without symbols",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }

    # Forbidden digit-string guard
    blob = json.dumps(report, ensure_ascii=False)
    forbidden = "44" + "31"
    if forbidden in blob:
        raise SystemExit(f"refusing to write forbidden token {forbidden!r}")

    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_notes(report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "seeds": report["seed_entries"],
                "graph_nodes": graph["node_count"],
                "graph_edges": graph["edge_count"],
                "arm_ops": len(arm_ordered),
                "label_order": hub_label_order,
                "hub_callees": callees_from_hub[:12],
                "opcode_summary": op_summary,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
