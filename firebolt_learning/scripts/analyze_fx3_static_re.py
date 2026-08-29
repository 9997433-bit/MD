#!/usr/bin/env python3
"""Static RE helpers for Firebolt FX3 image (no USB capture).

Extracts USB descriptor tree, string-xref candidates, and ARM immediates
near FPGA/Fusion anchors. Learning package only — not a full decompiler.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware" / "niusbFirebolt.cfg"
OUT = ROOT / "manifests" / "fx3_static_re.json"

# File-offset → VA addend. Empirically 0x3FFD6000 maps tFPGARegisterAccess
# string at file 0x4624c → VA 0x4001C24C (inside FX3 SYSMEM).
CANDIDATE_BASES = [0x3FFD6000, 0x40000000, 0x40003000, 0x00000100 - 0x0C, 0x00000000]


def parse_usb_descriptors(data: bytes, start: int) -> dict:
    """Walk descriptor chain starting at device descriptor offset."""
    out: dict = {"start": start, "device": None, "configurations": [], "interfaces": [], "endpoints": []}
    if start < 0 or start + 18 > len(data):
        return out
    d = data[start : start + 18]
    if d[0] != 0x12 or d[1] != 0x01:
        return out
    out["device"] = {
        "bcdUSB": f"0x{struct.unpack_from('<H', d, 2)[0]:04x}",
        "bDeviceClass": d[4],
        "bMaxPacketSize0": d[7],
        "idVendor": f"0x{struct.unpack_from('<H', d, 8)[0]:04x}",
        "idProduct": f"0x{struct.unpack_from('<H', d, 10)[0]:04x}",
        "bcdDevice": f"0x{struct.unpack_from('<H', d, 12)[0]:04x}",
        "bNumConfigurations": d[17],
    }
    # Scan a window after device descriptor for config/iface/ep
    window = data[start : min(len(data), start + 4096)]
    i = 18
    while i + 2 <= len(window):
        blen, btype = window[i], window[i + 1]
        if blen < 2 or i + blen > len(window):
            i += 1
            continue
        chunk = window[i : i + blen]
        if btype == 0x02 and blen >= 9:  # configuration
            out["configurations"].append(
                {
                    "offset": start + i,
                    "wTotalLength": struct.unpack_from("<H", chunk, 2)[0],
                    "bNumInterfaces": chunk[4],
                    "bConfigurationValue": chunk[5],
                    "bmAttributes": f"0x{chunk[7]:02x}",
                    "bMaxPower_2mA": chunk[8],
                }
            )
        elif btype == 0x04 and blen >= 9:  # interface
            out["interfaces"].append(
                {
                    "offset": start + i,
                    "bInterfaceNumber": chunk[2],
                    "bAlternateSetting": chunk[3],
                    "bNumEndpoints": chunk[4],
                    "bInterfaceClass": chunk[5],
                    "bInterfaceSubClass": chunk[6],
                    "bInterfaceProtocol": chunk[7],
                }
            )
        elif btype == 0x05 and blen >= 7:  # endpoint
            out["endpoints"].append(
                {
                    "offset": start + i,
                    "bEndpointAddress": f"0x{chunk[2]:02x}",
                    "direction": "IN" if chunk[2] & 0x80 else "OUT",
                    "number": chunk[2] & 0x0F,
                    "bmAttributes": f"0x{chunk[3]:02x}",
                    "xfer": {0: "control", 1: "iso", 2: "bulk", 3: "interrupt"}.get(
                        chunk[3] & 0x03, "other"
                    ),
                    "wMaxPacketSize": struct.unpack_from("<H", chunk, 4)[0],
                    "bInterval": chunk[6],
                }
            )
        i += blen
    return out


def find_string_file_offsets(data: bytes, needles: list[bytes]) -> dict[str, int]:
    found = {}
    for n in needles:
        i = data.find(n)
        if i >= 0:
            found[n.decode("latin1", "replace")] = i
    return found


def score_base(data: bytes, string_offs: dict[str, int], base: int) -> int:
    """Count LE pointers in image that match file_offset + base for known strings."""
    hits = 0
    for off in string_offs.values():
        ptr = struct.pack("<I", (base + off) & 0xFFFFFFFF)
        hits += data.count(ptr)
    return hits


def disasm_around_xrefs(
    data: bytes, string_offs: dict[str, int], base: int, window: int = 64
) -> list[dict]:
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
    md.detail = False
    results = []
    for name, off in string_offs.items():
        ptr = struct.pack("<I", (base + off) & 0xFFFFFFFF)
        xref_at = []
        start = 0
        while True:
            j = data.find(ptr, start)
            if j < 0:
                break
            if j % 4 == 0:
                xref_at.append(j)
            start = j + 1
            if len(xref_at) >= 8:
                break
        for xa in xref_at[:4]:
            # disassemble preceding words (literal pool often after code)
            code_off = max(0, xa - window)
            code_off -= code_off % 4
            chunk = data[code_off:xa]
            insns = []
            immediates = []
            for insn in md.disasm(chunk, base + code_off):
                insns.append(f"0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")
                # collect #imm and =0x... style
                if "#" in insn.op_str:
                    for part in insn.op_str.replace(",", " ").split():
                        if part.startswith("#"):
                            immediates.append(part)
            results.append(
                {
                    "string": name,
                    "string_file_off": off,
                    "ptr_va": f"0x{(base + off) & 0xFFFFFFFF:08x}",
                    "xref_file_off": xa,
                    "insns_before_literal": insns[-12:],
                    "immediates": immediates[-20:],
                }
            )
    return results


def collect_fpga_imm_histogram(xrefs: list[dict]) -> dict:
    """Histogram small immediates that might be register offsets (heuristic only)."""
    hist: dict[str, int] = {}
    for x in xrefs:
        if "FPGA" not in x["string"] and "Fusion" not in x["string"] and "fpga" not in x["string"].lower():
            if "tFPGA" not in x["string"] and "fusion" not in x["string"].lower():
                continue
        for imm in x.get("immediates", []):
            hist[imm] = hist.get(imm, 0) + 1
    # keep top
    top = sorted(hist.items(), key=lambda kv: -kv[1])[:40]
    return {"note": "heuristic only — not a proven register map", "top_immediates": top}


def main() -> None:
    data = FW.read_bytes()
    # device descriptor known from prior scan
    dev_off = data.find(bytes.fromhex("12011002000000402339447b"))
    usb = parse_usb_descriptors(data, dev_off)

    needles = [
        b"source/nimarengoSrc/tFPGARegisterAccess.c",
        b"source/nimarengoSrc/startup/tFPGA.c",
        b"source/nimarengoCore/fusion2/tFusionManager.c",
        b"source/nimarengoCore/tDMAManager.c",
        b"01_DMA_THREAD",
        b"03_PIB_THREAD",
        b"45:Counter Data Monitor handler",
        b"43:State Machine handler",
        b"Fusion",
    ]
    soffs = find_string_file_offsets(data, needles)
    base_scores = {f"0x{b:08x}": score_base(data, soffs, b) for b in CANDIDATE_BASES}
    best_base = max(CANDIDATE_BASES, key=lambda b: score_base(data, soffs, b))
    xrefs = disasm_around_xrefs(data, soffs, best_base)
    imm = collect_fpga_imm_histogram(xrefs)

    # Bulk endpoint summary for learning
    bulk_eps = [e for e in usb.get("endpoints", []) if e.get("xfer") == "bulk"]
    learning = {
        "usb_control_plane": (
            "Interface class 255 vendor-specific; Fusion vendor requests expected on EP0"
        ),
        "usb_data_plane_hypothesis": (
            "15 bulk + 1 interrupt endpoints → multi-pipe DMA / Signal Stream shape; "
            "frame layout still unknown (forced null)"
        ),
        "usb2_descriptor_caveat": (
            "bcdUSB 0x0210 and wMaxPacketSize 64 are what this image embeds; "
            "product may still enumerate SS at runtime — do not over-claim"
        ),
        "best_load_base_heuristic": f"0x{best_base:08x}",
        "base_scores": base_scores,
        "sync_not_in_fx3": True,
        "regmap_status": "unknown — immediates listed are candidates only",
        "see_also": ["docs/DATA_PATH.md", "docs/fx3_role_map.md"],
    }

    out = {
        "schema": "firebolt_learning.fx3_static_re.v1",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "usb_descriptors": usb,
        "bulk_endpoint_count": len(bulk_eps),
        "bulk_endpoints": bulk_eps,
        "string_file_offsets": soffs,
        "load_base_heuristic": learning["best_load_base_heuristic"],
        "load_base_scores": base_scores,
        "xref_samples": xrefs[:24],
        "fpga_fusion_immediate_histogram": imm,
        "learning": learning,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "dev_off": dev_off,
                "configs": len(usb["configurations"]),
                "ifaces": len(usb["interfaces"]),
                "eps": len(usb["endpoints"]),
                "bulk": len(bulk_eps),
                "base": learning["best_load_base_heuristic"],
                "xref_n": len(xrefs),
            }
        )
    )


if __name__ == "__main__":
    main()
