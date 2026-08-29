#!/usr/bin/env python3
"""Shape of FX3↔FPGA access path (PIB config), without fabric regmap."""
from __future__ import annotations

import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "niusbFirebolt.cfg"
OUT = ROOT / "manifests" / "fx3_regaccess_shape.json"
BASE = 0x3FFD6000


def main() -> None:
    data = FW.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)

    # PIB init @ 0x4001250c — first literal is 0xE0011000
    pool_va = 0x40012510 + 8 + 0xFC
    pib_cfg_base = struct.unpack_from("<I", data, pool_va - BASE)[0]

    stores = []
    fo = 0x4001250C - BASE
    for insn in md.disasm(data[fo : fo + 0x120], 0x4001250C):
        if insn.mnemonic == "str" and "[" in insn.op_str and "#" in insn.op_str:
            stores.append({"va": f"0x{insn.address:08X}", "op": insn.op_str})
        if insn.mnemonic == "pop" and "pc" in insn.op_str:
            break

    # Parse imm offsets where Rn appears as r3 (config base)
    offsets = []
    for s in stores:
        op = s["op"]
        if "[r3," in op and "#" in op:
            imm = op.split("#", 1)[1].rstrip("]")
            try:
                offsets.append(int(imm, 0))
            except ValueError:
                pass

    tags = {
        "file_region": "0x46180",
        "names": ["Op", "Fpga", "Fusion", "Trace"],
        "note": "Adjacent to Main Thread / State Machine handler strings; logging or subsystem enum candidates",
        "status": "candidate",
    }

    cfg_object = {
        "example_func_va": "0x400113D0",
        "fields": [
            {"offset": "0x00", "access": "ldrh", "note": "checked != 0"},
            {"offset": "0x04", "access": "ldr", "note": "word/ptr"},
            {"offset": "0x08", "access": "ldr", "note": "word/ptr"},
            {"offset": "0x0C", "access": "ldrh", "note": "u16"},
            {"offset": "0x10", "access": "ldr", "note": "word"},
            {"offset": "0x14", "access": "ldrh", "note": "compared to 0/1 (mode or count)"},
            {"offset": "0x18", "access": "ldr", "note": "nested ptr; [p+4] bits 0xc tested"},
        ],
        "status": "candidate",
        "interpretation": "GPIF/DMA configuration object walker — not AI channel map",
    }

    out = {
        "schema": "firebolt_learning.fx3_regaccess_shape.v1",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "pib_config_block": {
            "base": f"0x{pib_cfg_base:08X}",
            "init_func_va": "0x4001250C",
            "store_offsets_sorted": sorted(set(offsets)),
            "store_count": len(offsets),
            "status": "confirmed",
            "meaning": "FX3 PIB/GPIF configuration MMIO block (socket/engine setup)",
        },
        "subsystem_tags": tags,
        "gpif_cfg_object": cfg_object,
        "boundary": {
            "is_fpga_fabric_regmap": False,
            "fx3_regmap_status": "unknown",
            "why": (
                "Recovered PIB config offsets and GPIF object field shapes only. "
                "Fabric-side AIConv/sample-clock registers are not identified."
            ),
        },
        "learning": {
            "access_path": "Fusion/host → FX3 ARM → PIB@0xE0011000 / sockets → GPIF → FPGA",
            "next_static_step": "Ghidra on tFPGARegisterAccess callers with this PIB base as landmark",
            "next_dynamic_step": "USB capture for Fusion requests that trigger these PIB writes",
        },
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "pib_cfg_base": f"0x{pib_cfg_base:08X}",
                "offsets": len(set(offsets)),
                "tags": tags["names"],
            }
        )
    )


if __name__ == "__main__":
    main()
