#!/usr/bin/env python3
"""Parse Xilinx MCS (Intel HEX) and report structure. Stage L2 helper."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_mcs(path: Path) -> bytearray:
    segments: dict[int, bytes] = {}
    upper = 0
    with path.open("r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line.startswith(":") or len(line) < 11:
                continue
            count = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            rectype = int(line[7:9], 16)
            payload = bytes.fromhex(line[9 : 9 + count * 2])
            if rectype == 4 and count == 2:
                upper = ((payload[0] << 8) | payload[1]) << 16
            elif rectype == 0:
                base = upper + addr
                segments[base] = segments.get(base, b"") + payload
    if not segments:
        return bytearray()
    max_addr = max(base + len(payload) for base, payload in segments.items())
    data = bytearray(b"\xff" * (max_addr + 16))
    for base, payload in segments.items():
        data[base : base + len(payload)] = payload
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mcs", type=Path)
    ap.add_argument("--extract-bin", type=Path, default=None)
    args = ap.parse_args()

    data = parse_mcs(args.mcs)
    print(f"file: {args.mcs}")
    print(f"span_bytes: {len(data)}")
    print(f"non_ff_bytes: {sum(1 for b in data if b != 0xFF)}")

    sync = data.find(bytes.fromhex("aa995566"))
    boot = data.find(bytes.fromhex("000000bb11220044"))
    print(f"sync_aa995566_offset: {sync}")
    print(f"boot_bb11220044_offset: {boot}")

    idcodes = {
        0x03631093: "XC7K160T",
        0x0362C093: "XC7K325T",
        0x03722093: "XC7K70T",
        0x02824093: "XC3S200",
    }
    for code, name in idcodes.items():
        off = data.find(code.to_bytes(4, "big"))
        print(f"idcode_{name}: {off if off >= 0 else 'NOT_FOUND'}")

    # ASCII clues
    clues = []
    for m in re.finditer(rb"[\x20-\x7e]{8,}", bytes(data[: min(len(data), 8 * 1024 * 1024)])):
        s = m.group().decode("ascii", "ignore")
        if any(k in s.lower() for k in ("xilinx", "user", "date", "2023", "kintex", "vivado")):
            clues.append(s)
    print(f"ascii_clues: {clues[:20]}")
    print(f"bb11220044_count: {data.count(bytes.fromhex('000000bb11220044'))}")
    print(f"aa995566_count: {data.count(bytes.fromhex('aa995566'))}")

    if args.extract_bin:
        args.extract_bin.write_bytes(data)
        print(f"wrote_bin: {args.extract_bin} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
