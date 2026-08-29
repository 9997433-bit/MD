#!/usr/bin/env python3
"""Generate Firebolt static learning ledger from firmware + catalogs (no PE/USB capture)."""
from __future__ import annotations

import hashlib
import json
import re
import struct
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware"
MANIFESTS = ROOT / "manifests"
SIXFOUR = "https://github.com/Montyzhang/sixfour"

# Photo filenames as published in Montyzhang/sixfour (remote index; not vendored by default)
PHOTO_NAMES = [
    "微信图片_20260826133630_103_144.jpg",
    "微信图片_20260826133630_104_144.jpg",
    "微信图片_20260826133630_105_144.jpg",
    "微信图片_20260826133630_106_144.jpg",
    "微信图片_20260826133630_107_144.jpg",
    "微信图片_20260826133630_108_144.jpg",
    "微信图片_20260826133630_109_144.jpg",
    "微信图片_20260826133630_110_144.jpg",
    "微信图片_20260826133646_111_144.jpg",
    "微信图片_20260826133646_112_144.jpg",
    "微信图片_20260826133646_113_144.jpg",
    "微信图片_20260826133646_114_144.jpg",
    "微信图片_20260826133646_115_144.jpg",
    "微信图片_20260826133646_116_144.jpg",
    "微信图片_20260826133646_117_144.jpg",
    "微信图片_20260826133646_118_144.jpg",
    "微信图片_20260826133646_119_144.jpg",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    import math

    return -sum((v / n) * math.log2(v / n) for v in c.values())


def analyze_fx3(path: Path) -> dict:
    data = path.read_bytes()
    meta: dict = {
        "path": str(path.relative_to(ROOT)),
        "size": len(data),
        "sha256": sha256_file(path),
        "magic": data[:4].hex() if len(data) >= 4 else "",
        "cy_header": data[:2] == b"CY",
        "image_ctrl_bytes": list(data[2:4]) if len(data) >= 4 else [],
    }
    # USB device descriptor heuristic
    vid = pid = None
    for i in range(len(data) - 18):
        if data[i] == 0x12 and data[i + 1] == 0x01 and data[i + 3] == 0x02:
            vid = struct.unpack_from("<H", data, i + 8)[0]
            pid = struct.unpack_from("<H", data, i + 10)[0]
            meta["device_descriptor_offset"] = i
            meta["bcdUSB"] = struct.unpack_from("<H", data, i + 2)[0]
            break
    meta["idVendor"] = vid
    meta["idProduct"] = pid

    strs = re.findall(rb"[\x20-\x7e]{6,}", data)
    interesting = []
    keys = (
        b"source/",
        b"ThreadX",
        b"Fusion",
        b"FPGA",
        b"DMA",
        b"handler",
        b"Thread",
        b"nimarengo",
        b"Counter",
    )
    for s in strs:
        if any(k in s for k in keys):
            interesting.append(s.decode("latin1"))
    meta["anchor_strings"] = sorted(set(interesting))[:80]
    meta["entropy"] = round(entropy(data), 3)
    return meta


def analyze_bitstream(path: Path) -> dict:
    data = path.read_bytes()
    meta: dict = {
        "path": str(path.relative_to(ROOT)),
        "size": len(data),
        "sha256": sha256_file(path),
        "entropy": round(entropy(data), 3),
        "format": "xilinx_7series_bin",
    }
    sync = data.find(b"\xaa\x99\x55\x66")
    meta["sync_offset"] = sync
    idcode = None
    if sync >= 0:
        i = sync + 4
        end = min(len(data), sync + 4 + 256)
        while i + 4 <= end:
            w = struct.unpack_from(">I", data, i)[0]
            typ = (w >> 29) & 7
            if typ == 1:
                op = (w >> 27) & 3
                reg = (w >> 13) & 0x3FFF
                cnt = w & 0x7FF
                i += 4
                if op == 2 and cnt == 1 and i + 4 <= len(data):
                    val = struct.unpack_from(">I", data, i)[0]
                    if reg == 12:  # IDCODE
                        idcode = val
                    i += 4
                elif op == 2 and 0 < cnt < 16:
                    i += 4 * cnt
                else:
                    continue
            else:
                i += 4
    meta["idcode"] = f"0x{idcode:08X}" if idcode is not None else None
    meta["idcode_device"] = "XC7A100T" if idcode == 0x0362C093 else None
    lead_ff = 0
    while lead_ff < len(data) and data[lead_ff] == 0xFF:
        lead_ff += 1
    meta["leading_ff"] = lead_ff
    return meta


def build_photo_index() -> dict:
    photos = []
    local_dir = ROOT / "hardware" / "photos"
    for name in PHOTO_NAMES:
        local = local_dir / name
        entry = {
            "name": name,
            "source_url": f"{SIXFOUR}/blob/main/{name}",
            "vendored": local.exists(),
        }
        if local.exists():
            entry["sha256"] = sha256_file(local)
            entry["size"] = local.stat().st_size
        photos.append(entry)
    return {
        "source_repo": SIXFOUR,
        "policy": "photos not vendored by default; fetch into hardware/photos/ if needed",
        "count": len(photos),
        "photos": photos,
    }


def build_system_map() -> dict:
    return {
        "generated_by": "generate_ledger.py",
        "product": "NI USB-6453 / Firebolt",
        "node_count": 6,
        "edge_count": 5,
        "nodes": [
            {
                "id": "NODE-AI-IN",
                "layer": "hw",
                "name": "Analog inputs AI0..31",
                "status": "confirmed",
                "evidence": ["SPEC-PRODUCT-USB-6453", "HW-ADC-ARRAY"],
            },
            {
                "id": "NODE-ADC16",
                "layer": "hw",
                "name": "16× ADC (shared-clock convert)",
                "status": "confirmed",
                "evidence": ["SPEC-ADC-16", "SPEC-SYNC-LAYER", "HW-SYNC-LOCUS"],
            },
            {
                "id": "NODE-FPGA",
                "layer": "bit",
                "name": "Artix-7 XC7A100T fabric",
                "status": "confirmed",
                "evidence": ["BIT-IDCODE", "HW-FPGA-XC7A100T"],
            },
            {
                "id": "NODE-FX3",
                "layer": "fw",
                "name": "CYUSB3014 FX3 (ThreadX)",
                "status": "confirmed",
                "evidence": ["FX3-IMG-CY-MAGIC", "FX3-USB-VIDPID", "FX3-ROLE-SUMMARY"],
            },
            {
                "id": "NODE-USB",
                "layer": "bus",
                "name": "USB3 Signal Stream + Fusion control",
                "status": "candidate",
                "evidence": ["SPEC-XFER-STREAM", "FX3-FUSION", "FX3-DMA"],
            },
            {
                "id": "NODE-HOST",
                "layer": "host",
                "name": "NI-DAQmx / LabVIEW (out of scope)",
                "status": "not_started",
                "evidence": [],
            },
        ],
        "edges": [
            {"from": "NODE-AI-IN", "to": "NODE-ADC16", "via": "analog", "status": "confirmed"},
            {
                "from": "NODE-ADC16",
                "to": "NODE-FPGA",
                "via": "parallel_samples_shared_clock",
                "status": "confirmed",
            },
            {
                "from": "NODE-FPGA",
                "to": "NODE-FX3",
                "via": "GPIF_PIB_sockets_0xE0010000",
                "status": "confirmed",
            },
            {
                "from": "NODE-FX3",
                "to": "NODE-USB",
                "via": "USB3",
                "status": "candidate",
            },
            {
                "from": "NODE-USB",
                "to": "NODE-HOST",
                "via": "Fusion_and_SignalStream",
                "status": "not_started",
            },
        ],
        "mermaid": (
            "flowchart LR\n"
            "  NODE-AI-IN -->|analog| NODE-ADC16\n"
            "  NODE-ADC16 -->|shared convert clock| NODE-FPGA\n"
            "  NODE-FPGA -->|GPIF/regs candidate| NODE-FX3\n"
            "  NODE-FX3 -->|USB3| NODE-USB\n"
            "  NODE-USB -->|not_started| NODE-HOST\n"
        ),
    }


def build_ledger(fx3: dict, bit: dict) -> dict:
    from catalogs.catalog_bitstream import build_entries as bit_entries
    from catalogs.catalog_fx3 import build_entries as fx3_entries
    from catalogs.catalog_hw import build_entries as hw_entries
    from catalogs.catalog_learn import build_entries as learn_entries
    from catalogs.catalog_spec_sync import build_entries as spec_entries

    catalogs = {
        "spec": spec_entries(),
        "hardware": hw_entries(),
        "fx3": fx3_entries(),
        "bitstream": bit_entries(),
        "learn": learn_entries(),
    }
    flat = [e for block in catalogs.values() for e in block]
    status_counts: dict[str, int] = {}
    for e in flat:
        status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1

    return {
        "schema": "firebolt_learning.EvidenceLedger.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product": {
            "name": "NI USB-6453",
            "codename": "Firebolt",
            "source_repo": SIXFOUR,
            "usb": {"idVendor": fx3.get("idVendor"), "idProduct": fx3.get("idProduct")},
            "fpga_idcode": bit.get("idcode"),
            "fpga_device": bit.get("idcode_device"),
        },
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "phase": "static_skeleton_no_capture",
        "catalogs": catalogs,
        "stats": {
            "identifier_count": len(flat),
            "by_status": status_counts,
            "by_block": {k: len(v) for k, v in catalogs.items()},
        },
    }


def build_coverage(ledger: dict, bridge: dict) -> dict:
    return {
        "generated_at": ledger["generated_at"],
        "identifier_count": ledger["stats"]["identifier_count"],
        "by_status": ledger["stats"]["by_status"],
        "by_block": ledger["stats"]["by_block"],
        "forced_null_bridge_count": len(bridge.get("forced_null_bridges", [])),
        "stop_condition": {
            "catalog_complete": True,
            "vendor_equivalent": False,
            "runtime_behavior_mastered": False,
            "usb_capture_done": False,
        },
        "next_upgrades": [
            "USB capture for Fusion requests",
            "Ghidra on FX3 register access",
            "FPGA netlist / lab for sync clock tree",
        ],
    }


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    import sys

    sys.path.insert(0, str(ROOT))

    fx3_path = FW / "niusbFirebolt.cfg"
    bit_path = FW / "niusbFireboltFPGA.cfg"
    if not fx3_path.exists() or not bit_path.exists():
        raise SystemExit(f"missing firmware under {FW}")

    fx3 = analyze_fx3(fx3_path)
    bit = analyze_bitstream(bit_path)

    files = []
    for p in sorted(FW.glob("*")):
        if p.is_file():
            files.append(
                {
                    "path": str(p.relative_to(ROOT)),
                    "size": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )

    write_json(MANIFESTS / "manifest_files.json", {"files": files, "source_repo": SIXFOUR})
    write_json(
        MANIFESTS / "file_hashes.json",
        {f["path"]: f["sha256"] for f in files},
    )
    write_json(MANIFESTS / "firmware_meta.json", fx3)
    write_json(MANIFESTS / "bitstream_meta.json", bit)
    write_json(MANIFESTS / "photo_index.json", build_photo_index())
    write_json(MANIFESTS / "system_map.json", build_system_map())

    bridge = json.loads((ROOT / "bridge_matrix.json").read_text(encoding="utf-8"))
    ledger = build_ledger(fx3, bit)
    write_json(ROOT / "EvidenceLedger.json", ledger)
    coverage = build_coverage(ledger, bridge)
    write_json(ROOT / "coverage.json", coverage)

    arch = ROOT / "ARCHITECTURE.md"
    sm = build_system_map()
    arch.write_text(
        "# 系统架构图（自动生成）\n\n"
        f"**生成时间**：{ledger['generated_at']}\n\n"
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为\n\n"
        "```mermaid\n"
        f"{sm['mermaid']}"
        "```\n\n"
        "## 节点\n\n"
        "| Node | Layer | Status |\n"
        "|------|-------|--------|\n"
        + "".join(
            f"| `{n['id']}` | {n['layer']} | {n['status']} |\n" for n in sm["nodes"]
        )
        + "\n证据来源：`manifests/system_map.json`\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "ok": True,
                "identifiers": ledger["stats"]["identifier_count"],
                "by_status": ledger["stats"]["by_status"],
                "vid_pid": [fx3.get("idVendor"), fx3.get("idProduct")],
                "idcode": bit.get("idcode"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
