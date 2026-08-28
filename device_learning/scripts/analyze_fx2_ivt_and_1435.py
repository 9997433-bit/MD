#!/usr/bin/env python3
"""Build interrupt-vector map + annotated walk of datapath hot routine 0x1435.

Writes:
  - manifests/fx2_ivt_map.json
  - manifests/fx2_routine_1435_annotation.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from disasm_8051_lite import disasm_region  # noqa: E402

RAM = ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin"
XREFS = ROOT / "manifests" / "fx2_ram_xrefs.json"
OUT_IVT = ROOT / "manifests" / "fx2_ivt_map.json"
OUT_ANN = ROOT / "manifests" / "fx2_routine_1435_annotation.json"

VECTORS = [
    (0x0000, "reset"),
    (0x0003, "IE0_ext0"),
    (0x000B, "TF0_timer0"),
    (0x0013, "IE1_ext1"),
    (0x001B, "TF1_timer1"),
    (0x0023, "serial_RI_TI"),
    (0x002B, "TF2_EXF2"),
    (0x0043, "USB_or_ext_hint"),
]

SFR = {
    0xE600: "CPUCS",
    0xE601: "IFCONFIG",
    0xE604: "FIFORESET",
    0xE610: "EP1OUTCFG",
    0xE611: "EP1INCFG",
    0xE613: "EP4CFG",
    0xE614: "EP6CFG",
    0xE6A1: "EP4CS",
    0xE6A2: "EP6CS",
}


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not RAM.exists():
        for out in (OUT_IVT, OUT_ANN):
            out.write_text(json.dumps({"generated_at": now, "status": "missing"}, indent=2) + "\n")
        print(json.dumps({"status": "missing"}))
        return

    data = RAM.read_bytes()
    ivt = []
    for off, name in VECTORS:
        if off + 3 > len(data):
            continue
        chunk = data[off : off + 3]
        entry = {"vector": name, "offset": f"0x{off:04x}", "bytes": chunk.hex()}
        if chunk[0] == 0x02:
            dest = (chunk[1] << 8) | chunk[2]
            entry["ljmp_dest"] = f"0x{dest:04x}"
            entry["kind"] = "LJMP"
            entry["confidence"] = "candidate"
        elif chunk[0] == 0x12:
            dest = (chunk[1] << 8) | chunk[2]
            entry["lcall_dest"] = f"0x{dest:04x}"
            entry["kind"] = "LCALL"
            entry["confidence"] = "hypothesis"
        else:
            # disassemble a few bytes for context
            entry["preview"] = [r["text"] for r in disasm_region(data, off, 8, max_insns=4)]
            entry["confidence"] = "hypothesis"
        ivt.append(entry)

    OUT_IVT.write_text(
        json.dumps(
            {
                "generated_at": now,
                "status": "scanned",
                "layer": "L1-IVT",
                "vectors": ivt,
                "source_note": "fx2_ram_from_enum.bin — NOT eeprom.bin",
                "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    # Annotate 0x1435 window: collect MOV DPTR SFR labels in order
    start, length = 0x1435, 0x200
    insns = disasm_region(data, start, length, max_insns=250)
    sfr_seq = []
    opcode_imm = []
    for row in insns:
        t = row["text"]
        if t.startswith("MOV DPTR,#0x"):
            imm = int(t.split("#0x", 1)[1][:4], 16)
            if imm in SFR:
                sfr_seq.append({"at": row["addr"], "imm": f"0x{imm:04x}", "label": SFR[imm]})
        if t.startswith("MOV A,#0x") or t.startswith("CJNE A,#0x"):
            imm = int(t.split("#0x", 1)[1][:2], 16)
            if imm in (0x01, 0x04, 0x05, 0x08, 0x09, 0x0A, 0x0B):
                opcode_imm.append({"at": row["addr"], "text": t, "imm": f"0x{imm:02x}"})

    ann = {
        "generated_at": now,
        "status": "annotated",
        "layer": "L4-L5",
        "routine_entry": "0x1435",
        "why": "Dominant owner for opcode 0x08 immediates AND top EP6/FIFO datapath score",
        "sfr_access_sequence": sfr_seq,
        "cmd_opcode_immediates_in_window": opcode_imm,
        "interpretation": (
            "Ordered SFR touches inside 0x1435 suggest endpoint/FIFO configuration "
            "co-located with opcode-0x08 immediate sites; treat as start/arm+datapath hub candidate only."
        ),
        "semantics": "unknown",
        "confidence": "candidate",
        "oracle_ref": "manifests/fx2_oracle_crosscheck.json",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT_ANN.write_text(json.dumps(ann, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ivt_ljmp": [v for v in ivt if v.get("kind") == "LJMP"],
                "sfr_seq_len": len(sfr_seq),
                "opcode_imm_in_1435": opcode_imm,
                "sfr_labels": [s["label"] for s in sfr_seq],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
