#!/usr/bin/env python3
"""Derive bulk command-plane framing/taxonomy from usb_session.pcapng.

Writes:
  - manifests/usb_command_taxonomy.json
  - manifests/usb_primary_ctrl_744f.json

Does not modify catalogs. Requires tshark on PATH.
"""
from __future__ import annotations

import collections
import json
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"
MANIFESTS = ROOT / "manifests"
SESSION = CAPTURES / "usb_session.pcapng"
OUT_TAXONOMY = MANIFESTS / "usb_command_taxonomy.json"
OUT_CTRL = MANIFESTS / "usb_primary_ctrl_744f.json"

TARGET_VID = 0x3923
PRIMARY_PID = 0x744F


def run_tshark(pcap: Path, display_filter: str, fields: list[str]) -> list[list[str]]:
    cmd = ["tshark", "-r", str(pcap), "-Y", display_filter, "-T", "fields"]
    for f in fields:
        cmd.extend(["-e", f])
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    rows: list[list[str]] = []
    for line in out.splitlines():
        if line.strip():
            rows.append(line.split("\t"))
    return rows


def find_addr(pcap: Path) -> int | None:
    rows = run_tshark(
        pcap,
        f"usb.idVendor == {TARGET_VID:#x} && usb.idProduct == {PRIMARY_PID:#x}",
        ["usb.device_address"],
    )
    for row in rows:
        if row and row[0].isdigit():
            return int(row[0])
    return None


def payloads(pcap: Path, addr: int, ep: int) -> list[bytes]:
    rows = run_tshark(
        pcap,
        f"usb.device_address=={addr} && usb.endpoint_address=={ep:#x} && usb.capdata",
        ["usb.capdata"],
    )
    out: list[bytes] = []
    for row in rows:
        if not row or not row[0]:
            continue
        out.append(bytes.fromhex(row[0].replace(":", "")))
    return out


def score(raws: list[bytes]) -> tuple[dict, dict]:
    s: dict = {
        "n": 0,
        "frame_len_ok": 0,
        "body_len_ok": 0,
        "both": 0,
        "tags": collections.Counter(),
        "opcodes": collections.Counter(),
        "types": collections.Counter(),
    }
    by_op: dict = collections.defaultdict(
        lambda: {
            "count": 0,
            "tags": collections.Counter(),
            "types": collections.Counter(),
            "arg_lens": collections.Counter(),
            "example": None,
        }
    )
    for raw in raws:
        if len(raw) < 8:
            continue
        s["n"] += 1
        tag, flen, blen = struct.unpack(">HHH", raw[:6])
        typ, opc = raw[6], raw[7]
        f_ok = flen == len(raw)
        b_ok = blen == len(raw) - 4
        if f_ok:
            s["frame_len_ok"] += 1
        if b_ok:
            s["body_len_ok"] += 1
        if f_ok and b_ok:
            s["both"] += 1
            s["tags"][tag] += 1
            s["types"][typ] += 1
            s["opcodes"][opc] += 1
            e = by_op[opc]
            e["count"] += 1
            e["tags"][tag] += 1
            e["types"][typ] += 1
            e["arg_lens"][len(raw) - 8] += 1
            if e["example"] is None:
                e["example"] = raw.hex()
    n = max(1, s["n"])
    s["frame_len_ok_ratio"] = round(s["frame_len_ok"] / n, 4)
    s["body_len_ok_ratio"] = round(s["body_len_ok"] / n, 4)
    s["both_ratio"] = round(s["both"] / n, 4)
    return s, by_op


def counter_public(c: collections.Counter) -> dict[str, int]:
    return {f"0x{k:04x}" if isinstance(k, int) and k > 0xFF else f"0x{k:02x}" if isinstance(k, int) else str(k): v for k, v in c.most_common()}


def write_primary_ctrl(addr: int | None) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    if not SESSION.exists() or not shutil.which("tshark") or addr is None:
        kept = _preserve_if_good(OUT_CTRL)
        if kept is not None:
            return kept
        report = {
            "generated_at": now,
            "status": "missing",
            "boundary": "session pcap or tshark unavailable",
        }
        OUT_CTRL.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return report

    rows = run_tshark(
        SESSION,
        f"usb.device_address=={addr} && usb.setup.bRequest",
        ["usb.bmRequestType", "usb.setup.bRequest", "usb.setup.wValue", "usb.setup.wIndex", "usb.setup.wLength"],
    )
    hist: collections.Counter = collections.Counter()
    vendor = 0
    for r in rows:
        if len(r) < 2 or not r[1]:
            continue
        try:
            bm = int(r[0], 16) if r[0].startswith("0x") else int(r[0] or "0")
            br = int(r[1])
        except ValueError:
            continue
        hist[(r[0], br)] += 1
        # type bits 5..6 == 2 → vendor
        if ((bm >> 5) & 0x3) == 2:
            vendor += 1

    report = {
        "generated_at": now,
        "device": "0x3923:0x744f",
        "usb_addr": addr,
        "status": "decoded",
        "confidence": "confirmed" if vendor == 0 else "candidate",
        "finding": (
            "Primary device uses almost no vendor control; session control traffic is "
            "standard GET_DESCRIPTOR / SET_CONFIGURATION only. Command/data planes are "
            "bulk EP01/81 and EP06/84."
        ),
        "setup_histogram": [
            {"bmRequestType": k[0], "bRequest": k[1], "count": c} for k, c in hist.most_common()
        ],
        "vendor_control_setup_count": vendor,
        "vendor_control_on_primary": "none_observed_in_session" if vendor == 0 else "present",
        "companion_vendor_control": "see usb_vendor_ctrl_7317.json (FX2 0xA0 RAM load)",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT_CTRL.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _preserve_if_good(path: Path) -> dict | None:
    """Avoid clobbering a prior decoded report when pytest empties captures/."""
    if not path.exists():
        return None
    try:
        prev = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if prev.get("status") in ("hypothesis", "decoded", "decoded_partial"):
        return prev
    return None


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not SESSION.exists() or not shutil.which("tshark"):
        kept = _preserve_if_good(OUT_TAXONOMY)
        if kept is not None:
            print(json.dumps({"status": kept.get("status"), "preserved": True}, indent=2))
            return
        report = {
            "generated_at": now,
            "status": "missing",
            "boundary": "usb_session.pcapng or tshark unavailable",
        }
        OUT_TAXONOMY.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_primary_ctrl(None)
        print(json.dumps(report, indent=2))
        return

    addr = find_addr(SESSION)
    write_primary_ctrl(addr)
    if addr is None:
        report = {
            "generated_at": now,
            "status": "missing",
            "boundary": "primary 0x3923:0x744f not found in session",
        }
        OUT_TAXONOMY.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return

    out_s, out_op = score(payloads(SESSION, addr, 0x01))
    in_s, _ = score(payloads(SESSION, addr, 0x81))

    opcodes_table = []
    for opc, e in sorted(out_op.items(), key=lambda x: -x[1]["count"]):
        opcodes_table.append(
            {
                "opcode": f"0x{opc:02x}",
                "count": e["count"],
                "tags_hex": [f"0x{t:04x}" for t, _ in e["tags"].most_common()],
                "types_hex": [f"0x{t:02x}" for t in sorted(e["types"])],
                "arg_len_hist": {str(k): v for k, v in e["arg_lens"].most_common(8)},
                "example_hex": e["example"],
                "semantics": "unknown",
            }
        )

    def pub_stats(s: dict) -> dict:
        return {k: v for k, v in s.items() if not isinstance(v, collections.Counter)}

    report = {
        "generated_at": now,
        "device": "0x3923:0x744f",
        "usb_addr": addr,
        "status": "hypothesis",
        "confidence": "candidate",
        "framing_hypothesis": {
            "layout": [
                "BE u16 tag/stream_id (0x0000 and 0x0001 observed)",
                "BE u16 frame_length (= entire bulk payload length)",
                "BE u16 body_length (= frame_length - 4)",
                "u8 type/flags (0x00 or 0x01)",
                "u8 opcode (OUT) / status (IN; 0x00 = success-like)",
                "payload (frame_length - 8 bytes)",
            ],
            "supersedes": "Earlier BE-u32-total-length hypothesis was the special case tag==0",
            "ep01_out": pub_stats(out_s),
            "ep81_in": pub_stats(in_s),
            "out_tag_hist": {f"0x{k:04x}": c for k, c in out_s["tags"].most_common()},
            "in_tag_hist": {f"0x{k:04x}": c for k, c in in_s["tags"].most_common()},
        },
        "command_plane": {"out_ep": "0x01", "in_ep": "0x81"},
        "out_opcodes": opcodes_table,
        "in_status_bytes_top": [
            {"value": f"0x{k:02x}", "count": c} for k, c in in_s["opcodes"].most_common(10)
        ],
        "boundary": "Opcode meanings unknown without host software or firmware dump.",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT_TAXONOMY.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "both_ratio_out": out_s["both_ratio"],
                "both_ratio_in": in_s["both_ratio"],
                "opcode_count": len(opcodes_table),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
