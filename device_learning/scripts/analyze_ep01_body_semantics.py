#!/usr/bin/env python3
"""Deepen EP01/EP81 body-field hypotheses from usb_session.pcapng.

Infers candidate sub-TLVs under command bodies (often 0x0c-prefixed), pairs
OUT↔IN by frame tag, and scores channel-index / status patterns.

Writes manifests/ep01_body_semantics.json (max confidence: candidate).
"""
from __future__ import annotations

import collections
import json
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"
OUT = ROOT / "manifests" / "ep01_body_semantics.json"
VID, PID = 0x3923, 0x744F
PAIR_DT = 0.05


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


def parse_frame(raw: bytes) -> dict | None:
    if len(raw) < 8:
        return None
    tag, flen, blen = struct.unpack(">HHH", raw[:6])
    if flen != len(raw) or blen != len(raw) - 4:
        return None
    return {
        "tag": tag,
        "type": raw[6],
        "opcode": raw[7],
        "body": raw[8:],
        "raw_len": len(raw),
    }


def dissect_body(body: bytes) -> dict:
    """Heuristic: many bodies start with 0x0c | sub | u16be zeroish | payload."""
    info: dict = {"body_len": len(body), "hex": body.hex()}
    if len(body) >= 4 and body[0] == 0x0C:
        sub = body[1]
        info["tlv_prefix"] = f"0c{sub:02x}"
        info["subcode"] = f"0x{sub:02x}"
        rest = body[2:]
        # common: 0c03 0000 + u32 index
        if sub == 0x03 and len(body) >= 8:
            idx_le = struct.unpack("<I", body[4:8])[0]
            idx_be = struct.unpack(">I", body[4:8])[0]
            idx = idx_le if idx_le <= 7 else (body[4] if body[4] <= 7 else idx_be)
            info["u32_at_4_le"] = idx_le
            info["u32_at_4_be"] = idx_be
            if idx <= 3:
                info["channel_index_candidate"] = idx
        if sub == 0x0F and len(body) >= 12:
            info["u32_pair_be"] = [
                struct.unpack(">I", body[4:8])[0],
                struct.unpack(">I", body[8:12])[0],
            ]
            info["u32_pair_le"] = [
                struct.unpack("<I", body[4:8])[0],
                struct.unpack("<I", body[8:12])[0],
            ]
        if sub == 0x10 and len(body) >= 12:
            info["u32_at_4_le"] = struct.unpack("<I", body[4:8])[0]
            info["tail4_hex"] = body[8:12].hex()
            info["tail4_le_i32"] = struct.unpack("<i", body[8:12])[0]
            info["tail4_be_i32"] = struct.unpack(">i", body[8:12])[0]
        if sub == 0x20:
            info["role_guess"] = "status_or_capability_query_candidate"
        info["rest_hex"] = rest.hex()
    elif body == b"\x00\x00\x00\x00":
        info["role_guess"] = "empty_keepalive_body"
    return info


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    if not SESSION.exists():
        OUT.write_text(json.dumps({"generated_at": now, "status": "missing"}, indent=2) + "\n")
        print(json.dumps({"status": "missing"}))
        return

    addr = find_addr()
    if addr is None:
        OUT.write_text(json.dumps({"generated_at": now, "status": "missing", "note": "no addr"}, indent=2) + "\n")
        print(json.dumps({"status": "no_addr"}))
        return

    outs: list[tuple[float, dict]] = []
    for row in tshark(
        f"usb.device_address=={addr} && usb.endpoint_address==0x01 && usb.capdata",
        ["frame.time_relative", "usb.capdata"],
    ):
        raw = bytes.fromhex(row[1].replace(":", ""))
        fr = parse_frame(raw)
        if fr:
            outs.append((float(row[0]), fr))

    ins: list[tuple[float, dict]] = []
    for row in tshark(
        f"usb.device_address=={addr} && usb.endpoint_address==0x81 && usb.capdata",
        ["frame.time_relative", "usb.capdata"],
    ):
        raw = bytes.fromhex(row[1].replace(":", ""))
        fr = parse_frame(raw)
        if fr:
            ins.append((float(row[0]), fr))

    by_tag: dict[int, list[tuple[float, dict]]] = collections.defaultdict(list)
    for t, fr in ins:
        by_tag[fr["tag"]].append((t, fr))

    opcode_stats: dict[str, dict] = {}
    subcode_counts: collections.Counter = collections.Counter()
    channel_idx_counts: collections.Counter = collections.Counter()
    status_counts: collections.Counter = collections.Counter()
    paired = 0
    long_readbacks = []

    for t, fr in outs:
        op = fr["opcode"]
        key = f"0x{op:02x}"
        st = opcode_stats.setdefault(
            key,
            {
                "out_count": 0,
                "body_len_hist": collections.Counter(),
                "subcode_hist": collections.Counter(),
                "paired": 0,
                "in_status_hist": collections.Counter(),
                "in_body_len_hist": collections.Counter(),
                "examples": [],
            },
        )
        st["out_count"] += 1
        body = fr["body"]
        st["body_len_hist"][len(body)] += 1
        d = dissect_body(body)
        if "subcode" in d:
            st["subcode_hist"][d["subcode"]] += 1
            subcode_counts[d["subcode"]] += 1
        if "channel_index_candidate" in d:
            channel_idx_counts[d["channel_index_candidate"]] += 1

        # pair
        match = None
        for ti, ifr in by_tag.get(fr["tag"], []):
            if 0 <= ti - t <= PAIR_DT:
                match = (ti, ifr)
                break
        ex = {
            "t": t,
            "tag": fr["tag"],
            "type": fr["type"],
            "body_dissect": d,
        }
        if match:
            paired += 1
            st["paired"] += 1
            ib = match[1]["body"]
            status = ib[:4].hex() if len(ib) >= 4 else ib.hex()
            st["in_status_hist"][status] += 1
            st["in_body_len_hist"][len(ib)] += 1
            status_counts[status] += 1
            ex["in_dt"] = round(match[0] - t, 6)
            ex["in_body_hex"] = ib.hex()
            ex["in_status_u32_be"] = struct.unpack(">I", ib[:4])[0] if len(ib) >= 4 else None
            if len(ib) >= 16 and len(long_readbacks) < 8 and op == 0x08:
                long_readbacks.append(ex)
        if len(st["examples"]) < 4:
            st["examples"].append(ex)

    # finalize counters to plain dicts
    for st in opcode_stats.values():
        st["body_len_hist"] = {str(k): v for k, v in st["body_len_hist"].most_common()}
        st["subcode_hist"] = dict(st["subcode_hist"].most_common())
        st["in_status_hist"] = dict(st["in_status_hist"].most_common())
        st["in_body_len_hist"] = {str(k): v for k, v in st["in_body_len_hist"].most_common()}

    hypotheses = [
        {
            "id": "H_STATUS_OK_2",
            "statement": "EP81 body prefix u32be==2 is the dominant success/status code for paired replies",
            "support": f"{status_counts.get('00000002', 0)}/{paired} paired replies",
            "confidence": "candidate",
        },
        {
            "id": "H_KEEPALIVE_01",
            "statement": "opcode 0x01 OUT body 00000000 with IN status 2 is keepalive/poll",
            "support": opcode_stats.get("0x01", {}),
            "confidence": "candidate",
        },
        {
            "id": "H_BODY_0C_TLV",
            "statement": "Non-empty command bodies frequently use 0x0c|subcode|… vendor TLV",
            "support": dict(subcode_counts.most_common()),
            "confidence": "candidate",
        },
        {
            "id": "H_SUB_03_CHANNEL",
            "statement": "TLV subcode 0x03 carries u32 index 0..3 — channel select/config candidate",
            "support": {"index_hist": dict(channel_idx_counts), "note": "4 distinct indices match 4 AI channels"},
            "confidence": "candidate" if set(channel_idx_counts) >= {0, 1, 2, 3} else "hypothesis",
        },
        {
            "id": "H_SUB_0F_READBACK",
            "statement": "opcode 0x08 + sub 0x0f often yields longer EP81 bodies (config readback candidate)",
            "support": {"long_readback_examples": len(long_readbacks)},
            "confidence": "hypothesis",
        },
        {
            "id": "H_SUB_20_QUERY",
            "statement": "subcode 0x20 short body on 0x09 looks like status/capability query",
            "support": "frequent 0c200000 on opcode 0x09",
            "confidence": "hypothesis",
        },
    ]

    report = {
        "generated_at": now,
        "status": "hypothesized",
        "device": f"0x{VID:04x}:0x{PID:04x}",
        "usb_addr": addr,
        "ep01_out_count": len(outs),
        "ep81_in_count": len(ins),
        "paired_by_tag": paired,
        "pair_rate": round(paired / max(1, len(outs)), 4),
        "opcode_stats": opcode_stats,
        "subcode_counts": dict(subcode_counts.most_common()),
        "channel_index_candidate_hist": {str(k): v for k, v in sorted(channel_idx_counts.items())},
        "ep81_status_prefix_hist": dict(status_counts.most_common()),
        "long_readback_examples": long_readbacks,
        "hypotheses": hypotheses,
        "confidence_ceiling": "candidate",
        "boundary": "Field meanings inferred from passive traffic only; not stimulus-validated",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "paired": paired,
                "pair_rate": report["pair_rate"],
                "subcodes": report["subcode_counts"],
                "channel_idx": report["channel_index_candidate_hist"],
                "hypotheses": [h["id"] + ":" + h["confidence"] for h in hypotheses],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
