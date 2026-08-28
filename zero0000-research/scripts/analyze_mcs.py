#!/usr/bin/env python3
"""
MCS / Intel-HEX 固件结构分析脚本
用途：解析 Intel HEX 记录、重建线性镜像、定位 Xilinx 7-series 比特流特征字。
默认读本仓库 assets/firmware/20230825_s2056.mcs。
"""
from __future__ import annotations

import argparse
import collections
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_MCS = HERE.parent / "assets" / "firmware" / "20230825_s2056.mcs"

# UG470 / 实测：Kintex-7 160T 家族码为 0x0364C093（旧笔记 0x03631093 实为 Artix 误记）
IDCODES = {
    "XC7K160T": 0x0364C093,
    "XC7K70T": 0x03647093,
    "XC7K325T": 0x03651093,
    "XC7K410T": 0x03656093,
    "XC7A35T": 0x0362C093,
    "XC7A50T": 0x0362C093,
    "XC7A75T": 0x0362F093,
    "XC7A100T": 0x0362D093,
    "XC7A200T": 0x03636093,
    "XC7Z020": 0x03727093,
}


def find_all(buf: bytes, pat: bytes) -> list[int]:
    out: list[int] = []
    start = 0
    while True:
        i = buf.find(pat, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out


def entropy(buf: bytes) -> float:
    if not buf:
        return 0.0
    c = collections.Counter(buf)
    n = len(buf)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def parse_mcs(path: Path) -> tuple[bytearray, dict]:
    rec_types: collections.Counter = collections.Counter()
    data_bytes_total = 0
    ela_upper = 0
    min_addr = None
    max_addr = None
    flat = bytearray()
    expected_next = None
    gaps = []

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line[0] != ":":
                continue
            bytecount = int(line[1:3], 16)
            offset = int(line[3:7], 16)
            rtype = int(line[7:9], 16)
            data = bytes.fromhex(line[9 : 9 + bytecount * 2])
            raw = bytes.fromhex(line[1 : 9 + bytecount * 2 + 2])
            if (sum(raw) & 0xFF) != 0:
                print(f"[WARN] 行 {lineno} 校验和错误", file=sys.stderr)
            rec_types[rtype] += 1
            if rtype == 0x00:
                data_bytes_total += bytecount
                abs_addr = (ela_upper << 16) | offset
                if min_addr is None or abs_addr < min_addr:
                    min_addr = abs_addr
                end = abs_addr + bytecount
                if max_addr is None or end > max_addr:
                    max_addr = end
                if expected_next is not None and abs_addr != expected_next:
                    gaps.append((expected_next, abs_addr))
                flat.extend(data)
                expected_next = end
            elif rtype == 0x04:
                ela_upper = int.from_bytes(data, "big")

    meta = {
        "rec_types": rec_types,
        "data_bytes_total": data_bytes_total,
        "min_addr": min_addr,
        "max_addr": max_addr,
        "gaps": gaps,
    }
    return flat, meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze Xilinx MCS / Intel-HEX bitstream")
    ap.add_argument("mcs", nargs="?", type=Path, default=DEFAULT_MCS)
    args = ap.parse_args()
    if not args.mcs.is_file():
        print(f"MCS not found: {args.mcs}", file=sys.stderr)
        return 1

    flat, meta = parse_mcs(args.mcs)
    names = {
        0x00: "00 数据",
        0x01: "01 EOF",
        0x02: "02 扩展段地址",
        0x03: "03 起始段地址",
        0x04: "04 扩展线性地址",
        0x05: "05 起始线性地址",
    }
    print("=== Intel HEX 记录统计 ===")
    print(f"文件: {args.mcs}")
    for t, c in sorted(meta["rec_types"].items()):
        print(f"  {names.get(t, hex(t)):20s}: {c}")
    print(
        f"数据字节总量: {meta['data_bytes_total']} "
        f"(0x{meta['data_bytes_total']:X}) = {meta['data_bytes_total']/1024/1024:.3f} MiB"
    )
    print(f"地址范围: 0x{meta['min_addr']:08X} .. 0x{meta['max_addr']:08X}")
    print(f"重建连续镜像长度: {len(flat)} 字节")
    print(f"地址间隙数: {len(meta['gaps'])}")

    patterns = {
        "同步字 AA995566": bytes.fromhex("AA995566"),
        "boot header BB11220044": bytes.fromhex("BB11220044"),
        "总线宽度检测 000000BB": bytes.fromhex("000000BB"),
    }
    print("\n=== 特征字搜索 ===")
    for name, pat in patterns.items():
        hits = find_all(flat, pat)
        show = ", ".join(f"0x{h:X}" for h in hits[:8])
        print(f"  {name:26s}: {len(hits):6d} 处  {show}")

    print("\n=== 7-series IDCODE 扫描 ===")
    cmd = bytes.fromhex("30018001")
    for off in find_all(flat, cmd):
        val = int.from_bytes(flat[off + 4 : off + 8], "big")
        match = [k for k, v in IDCODES.items() if v == val]
        label = match[0] if match else "(未知/未匹配已知库)"
        print(f"  @0x{off:X}  IDCODE=0x{val:08X}  {label}")

    sync_hits = find_all(flat, bytes.fromhex("AA995566"))
    if sync_hits:
        body = flat[sync_hits[0] : sync_hits[0] + 0x100000]
        print(f"\n首个 sync 后 1MiB 熵: {entropy(body):.4f} bits/byte")

    ctl = bytes.fromhex("30008001")
    print("\n=== CTL0 (加密 DEC 位) 检查 ===")
    for off in find_all(flat, ctl)[:8]:
        val = int.from_bytes(flat[off + 4 : off + 8], "big")
        dec = "DEC=1(加密)" if val & 0x40 else "DEC=0(未加密)"
        print(f"  @0x{off:X}  CTL0=0x{val:08X}  {dec}")

    print("\n=== Flash 占用估计 ===")
    span = meta["max_addr"] - meta["min_addr"]
    print(f"  地址跨度: {span} 字节 ({span/1024/1024:.2f} MiB)")
    print(f"  sync 字出现次数(=候选镜像数): {len(sync_hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
