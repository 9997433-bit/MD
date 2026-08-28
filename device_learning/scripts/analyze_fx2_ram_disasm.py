#!/usr/bin/env python3
"""Disassemble priority FX2 RAM regions into mcu_disasm.txt + JSON index.

Not a substitute for Ghidra; advances BINARY_RE_PLAN G4 with reproducible text.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from disasm_8051_lite import disasm_region  # noqa: E402

RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
DISPATCH = ROOT / "manifests" / "fx2_cmd_dispatch_hypothesis.json"
DATAPATH = ROOT / "manifests" / "fx2_datapath_hypothesis.json"
OUT_TXT = ROOT / "phase_b" / "analysis" / "mcu_disasm.txt"
OUT_JSON = ROOT / "manifests" / "fx2_ram_disasm.json"

SFR = {
    0xE600: "CPUCS",
    0xE601: "IFCONFIG",
    0xE604: "FIFORESET",
    0xE610: "EP1OUTCFG",
    0xE611: "EP1INCFG",
    0xE612: "EP2CFG",
    0xE613: "EP4CFG",
    0xE614: "EP6CFG",
    0xE615: "EP8CFG",
    0xE6A0: "EP2CS",
    0xE6A1: "EP4CS",
    0xE6A2: "EP6CS",
    0xE6A3: "EP8CS",
}


def annotate(text: str) -> str:
    if "MOV DPTR,#0x" in text:
        try:
            imm = int(text.split("#0x", 1)[1][:4], 16)
        except ValueError:
            return text
        lab = SFR.get(imm)
        if lab:
            return f"{text}  ; {lab}"
    return text


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        OUT_JSON.write_text(
            json.dumps({"generated_at": now, "status": "missing"}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"status": "missing"}))
        return

    data = RAM.read_bytes()
    regions = [
        {"name": "reset_vector", "start": 0x0000, "length": 0x40},
        {"name": "main_init_0x075b", "start": 0x075B, "length": 0xA0},
        {"name": "hot_0x0393", "start": 0x0393, "length": 0x40},
        {"name": "cmd_0x01_owner_0x0473", "start": 0x0473, "length": 0xA0},
        {"name": "cmd_0x08_datapath_0x1435", "start": 0x1435, "length": 0x200},
        {"name": "cpucs_cluster_0x16ab", "start": 0x16AB, "length": 0x80},
    ]
    # append datapath followups
    if DATAPATH.exists():
        dp = json.loads(DATAPATH.read_text(encoding="utf-8"))
        for entry in (dp.get("primary_followups_for_ghidra") or [])[:6]:
            addr = int(entry, 16)
            name = f"datapath_{entry}"
            if not any(r["start"] == addr for r in regions):
                regions.append({"name": name, "start": addr, "length": 0x80})

    blocks = []
    lines = [
        "# MCU disassembly excerpt (lite 8051) — NOT full Ghidra output",
        f"# source: phase_b/analysis/fx2_ram_from_enum.bin sha256={hashlib.sha256(data).hexdigest()}",
        "# declaration: 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "# boundary: heuristic lengths; verify in Ghidra 8051",
        "",
    ]
    for reg in regions:
        insns = disasm_region(data, reg["start"], reg["length"])
        for row in insns:
            row["text"] = annotate(row["text"])
        blocks.append({**reg, "insn_count": len(insns), "insns": insns})
        lines.append(f"; ===== {reg['name']} @ 0x{reg['start']:04x} len={reg['length']} =====")
        for row in insns:
            lines.append(f"{row['addr']}: {row['bytes']:<8}  {row['text']}")
        lines.append("")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report = {
        "generated_at": now,
        "status": "partial_disasm",
        "layer": "G4-lite",
        "plan_ref": "BINARY_RE_PLAN.md",
        "path_txt": str(OUT_TXT.relative_to(ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "region_count": len(blocks),
        "regions": [{"name": b["name"], "start": f"0x{b['start']:04x}", "insn_count": b["insn_count"]} for b in blocks],
        "confidence": "hypothesis",
        "boundary": "Lite disassembler; not equivalent to Ghidra CFG",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "regions": report["regions"]}, indent=2))


if __name__ == "__main__":
    main()
