#!/usr/bin/env python3
"""L1–L2 bottom-up xrefs on FX2 RAM image (NOT eeprom.bin).

Scans:
  - LJMP/LCALL absolute targets
  - MOV DPTR,#imm16 immediate pool
  - bytes that look like IVT slots at classic 8051 vectors
  - code offsets near E6xx SFR immediates (heuristic)

Writes manifests/fx2_ram_xrefs.json.
"""
from __future__ import annotations

import hashlib
import json
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
OUT = ROOT / "manifests" / "fx2_ram_xrefs.json"

# Public FX2LP-ish SFR / XDATA names we care about (address → label).
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

# Classic 8051 interrupt vector bases (device may relocate; still useful scan anchors).
VECTORS = [
    (0x0000, "reset"),
    (0x0003, "IE0"),
    (0x000B, "TF0"),
    (0x0013, "IE1"),
    (0x001B, "TF1"),
    (0x0023, "RI_TI"),
    (0x002B, "TF2"),
    (0x0043, "USB_HINT"),  # FX2 USB often near here in many images — candidate only
]


def scan_abs_calls(data: bytes) -> list[dict]:
    """Opcode 0x02 LJMP abs, 0x12 LCALL abs."""
    hits: list[dict] = []
    for i in range(len(data) - 2):
        op = data[i]
        if op not in (0x02, 0x12):
            continue
        dest = (data[i + 1] << 8) | data[i + 2]
        if dest >= len(data):
            continue
        hits.append(
            {
                "at": f"0x{i:04x}",
                "op": "LJMP" if op == 0x02 else "LCALL",
                "dest": f"0x{dest:04x}",
            }
        )
    return hits


def scan_mov_dptr(data: bytes) -> list[dict]:
    """Opcode 0x90 MOV DPTR,#imm16 — common for XDATA/SFR window addressing."""
    hits: list[dict] = []
    for i in range(len(data) - 2):
        if data[i] != 0x90:
            continue
        imm = (data[i + 1] << 8) | data[i + 2]
        label = SFR_LABELS.get(imm)
        hits.append(
            {
                "at": f"0x{i:04x}",
                "imm": f"0x{imm:04x}",
                "label": label,
            }
        )
    return hits


def vector_snapshot(data: bytes) -> list[dict]:
    out = []
    for off, name in VECTORS:
        if off + 3 > len(data):
            continue
        chunk = data[off : off + 3]
        entry: dict = {"vector": name, "offset": f"0x{off:04x}", "bytes_hex": chunk.hex()}
        if chunk[0] == 0x02:
            dest = (chunk[1] << 8) | chunk[2]
            entry["ljmp_dest"] = f"0x{dest:04x}"
            entry["confidence"] = "candidate"
        else:
            entry["confidence"] = "hypothesis"
        out.append(entry)
    return out


def imm16_histogram(movs: list[dict]) -> list[dict]:
    c: Counter[str] = Counter()
    labels: dict[str, str | None] = {}
    for m in movs:
        c[m["imm"]] += 1
        labels[m["imm"]] = m.get("label")
    return [
        {"imm": imm, "count": n, "label": labels.get(imm)}
        for imm, n in c.most_common(40)
    ]


def opcode_imm_hits(data: bytes, opcodes: list[int]) -> dict[str, list[str]]:
    """Find code offsets comparing/loading known bulk opcodes as immediates."""
    found: dict[str, list[str]] = {f"0x{o:02x}": [] for o in opcodes}

    def add(key: str, at: int) -> None:
        if key in found and len(found[key]) < 40:
            found[key].append(f"0x{at:04x}")

    for i in range(len(data) - 1):
        op = data[i]
        imm = data[i + 1]
        key = f"0x{imm:02x}"
        # MOV/ADD/ADDC/ORL/ANL/XRL A,#imm and CJNE A,#imm
        if op in (0x74, 0x24, 0x34, 0x44, 0x54, 0x64, 0xB4):
            add(key, i)
        # CJNE @R0/#, @R1/#, Rn,#imm
        if op in (0xB6, 0xB7) or 0xB8 <= op <= 0xBF:
            add(key, i)
        # MOV Rn,#imm
        if 0x78 <= op <= 0x7F:
            add(key, i)
    return {k: v for k, v in found.items() if v}


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        report = {
            "generated_at": now,
            "status": "missing",
            "path": str(RAM.relative_to(ROOT)),
            "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        }
        OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    data = RAM.read_bytes()
    calls = scan_abs_calls(data)
    movs = scan_mov_dptr(data)
    dest_counts = Counter(h["dest"] for h in calls)
    hot_dests = [{"dest": d, "refs": n} for d, n in dest_counts.most_common(25)]

    sfr_movs = [m for m in movs if m.get("label")]
    cmd_opcodes = [0x01, 0x08, 0x09, 0x0A, 0x0B, 0x04, 0x05]

    report = {
        "generated_at": now,
        "status": "scanned",
        "layer": "L1-L2",
        "plan_ref": "BINARY_RE_PLAN.md",
        "path": str(RAM.relative_to(ROOT)),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "source_note": "Volatile FX2 RAM image from USB enum — NOT eeprom.bin",
        "vectors": vector_snapshot(data),
        "abs_branch_count": len(calls),
        "hot_abs_destinations": hot_dests,
        "mov_dptr_count": len(movs),
        "mov_dptr_imm_top": imm16_histogram(movs),
        "sfr_dptr_hits": sfr_movs[:80],
        "sfr_label_coverage": sorted({m["label"] for m in sfr_movs if m.get("label")}),
        "cmd_opcode_imm_sites": opcode_imm_hits(data, cmd_opcodes),
        "confidence": "candidate",
        "boundary": "Heuristic 8051 decode without full disassembler; false positives expected",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "next_layer": "L3 routine segmentation + Ghidra annotate from hot destinations and SFR hits",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "abs_branches": report["abs_branch_count"],
                "mov_dptr": report["mov_dptr_count"],
                "sfr_labels": report["sfr_label_coverage"],
                "reset": report["vectors"][0] if report["vectors"] else None,
                "top_dest": report["hot_abs_destinations"][:5],
                "opcode_imm_keys": list(report["cmd_opcode_imm_sites"].keys()),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
