#!/usr/bin/env python3
"""Prototype EP84 unpacker using the top structural packing candidate.

Default model: big-endian u32 words with seven low zero bits (>>7), no header.
Writes manifests/ep84_unpack_preview.json (candidate only — not calibrated volts).

Never claims confirmed semantics; requires usb_session.pcapng + tshark.
"""
from __future__ import annotations

import json
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"
PACK = ROOT / "manifests" / "ep84_packing_deep.json"
OUT = ROOT / "manifests" / "ep84_unpack_preview.json"
VID, PID = 0x3923, 0x744F
MAX_PAYLOADS = 8
MAX_WORDS_REPORT = 64


def tshark(filt: str, fields: list[str]) -> list[list[str]]:
    cmd = ["tshark", "-r", str(SESSION), "-Y", filt, "-T", "fields"]
    for f in fields:
        cmd.extend(["-e", f])
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [ln.split("\t") for ln in out.splitlines() if ln.strip()]


def find_addr() -> int | None:
    for row in tshark(f"usb.idVendor=={VID:#x} && usb.idProduct=={PID:#x}", ["usb.device_address"]):
        if row and row[0].isdigit():
            return int(row[0])
    return None


def unpack_be32_shift7(blob: bytes) -> list[int]:
    n = len(blob) - (len(blob) % 4)
    out = []
    for i in range(0, n, 4):
        w = struct.unpack_from(">I", blob, i)[0]
        out.append(w >> 7)
    return out


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not SESSION.exists():
        OUT.write_text(
            json.dumps({"generated_at": now, "status": "missing", "boundary": "no usb_session.pcapng"}, indent=2)
            + "\n"
        )
        print(json.dumps({"status": "missing"}))
        return

    pack = {}
    if PACK.exists():
        pack = json.loads(PACK.read_text(encoding="utf-8"))
    top = pack.get("top_hypothesis") or {
        "id": "P1_BE32_SHIFT7_SCALAR",
        "confidence": "candidate",
        "statement": "BE u32 >>7 headerless",
    }

    addr = find_addr()
    if addr is None:
        OUT.write_text(json.dumps({"generated_at": now, "status": "missing", "note": "device addr not found"}, indent=2) + "\n")
        print(json.dumps({"status": "no_addr"}))
        return

    rows = tshark(
        f"usb.device_address=={addr} && usb.endpoint_address==0x84 && usb.capdata",
        ["frame.time_relative", "usb.capdata"],
    )
    previews = []
    all_vals: list[int] = []
    for row in rows[:MAX_PAYLOADS]:
        if len(row) < 2 or not row[1]:
            continue
        raw = bytes.fromhex(row[1].replace(":", ""))
        vals = unpack_be32_shift7(raw)
        all_vals.extend(vals)
        previews.append(
            {
                "t": float(row[0]) if row[0] else None,
                "nbytes": len(raw),
                "nwords": len(vals),
                "first_words": vals[:MAX_WORDS_REPORT],
                "min": min(vals) if vals else None,
                "max": max(vals) if vals else None,
                "mean": (sum(vals) / len(vals)) if vals else None,
            }
        )

    report = {
        "generated_at": now,
        "status": "preview",
        "confidence": "candidate",
        "model": top,
        "device_addr": addr,
        "payloads_decoded": len(previews),
        "total_words_in_preview": len(all_vals),
        "global_min": min(all_vals) if all_vals else None,
        "global_max": max(all_vals) if all_vals else None,
        "global_mean": (sum(all_vals) / len(all_vals)) if all_vals else None,
        "previews": previews,
        "boundary": (
            "Structural unpack only; values are not volts, not calibrated, "
            "channel map unknown, signedness unproven"
        ),
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "preview",
                "payloads": len(previews),
                "words": len(all_vals),
                "min": report["global_min"],
                "max": report["global_max"],
                "mean": report["global_mean"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
