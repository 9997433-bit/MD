#!/usr/bin/env python3
"""
全量二进制普查（s2056）— 身份/熵/关键字/频率字面量/SPI 先验字/64KB 窗密度。

不替代 analyze_bitstream / search_spi_constants；本脚本给出一次可复现快照。

用法：
  python3 scripts/binary_full_census.py assets/firmware/20230825_s2056.bin
  python3 scripts/binary_full_census.py assets/firmware/20230825_s2056.bin --json out.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BIN = "7587ee1c0316f0be2e30c4fb934d24276701ffbc142f51b3d9e907c7b47615d1"

KEYS = [
    b"FFT",
    b"FIR",
    b"NCO",
    b"DDS",
    b"DDC",
    b"DUC",
    b"CIC",
    b"Xilinx",
    b"MicroBlaze",
    b"PicoBlaze",
    b"ADS62P49",
    b"DAC3283",
    b"CDCE72010",
    b"FT600",
    b"fmc150",
    b"FMC150",
    b"AXI",
    b"MIG",
    b"DDR3",
    b"Ethernet",
    b"Kintex",
]

FREQS = [
    b"245.76",
    b"491.52",
    b"122.88",
    b"61.44",
    b"163.84",
    b"245760000",
    b"491520000",
    b"122880000",
    b"61440000",
]

SPI_WORDS = {
    "conserviss_reg0": 0x683C0350,
    "conserviss_rega": 0x05FC270A,
    "rhino_reg2": 0x83040002,
    "e2e_reg0": 0x683C0340,
    "dac_cfg1_0121": 0x00000121,
    "nco_p12": 0x03200000,
    "nco_m12": 0x0CE00000,
}


def census(data: bytes) -> dict:
    hist = collections.Counter(data)
    n = len(data)
    ent = -sum((c / n) * math.log2(c / n) for c in hist.values())
    kw = {k.decode(): data.count(k) for k in KEYS}
    # DDS context note
    dds_ctx = []
    off = 0
    while True:
        i = data.find(b"DDS", off)
        if i < 0:
            break
        dds_ctx.append(
            {
                "off": hex(i),
                "ctx": data[max(0, i - 4) : i + 12].hex(),
            }
        )
        off = i + 1

    spi = {}
    for name, v in SPI_WORDS.items():
        spi[name] = {
            "BE": data.count(struct.pack(">I", v)),
            "LE": data.count(struct.pack("<I", v)),
        }

    wins = []
    W = 65536
    for o in range(0, n, W):
        chunk = data[o : o + W]
        nz = sum(1 for b in chunk if b)
        wins.append({"off": hex(o), "nz_pct": round(100 * nz / len(chunk), 1)})

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "bin_len": n,
        "bin_sha256": hashlib.sha256(data).hexdigest(),
        "sync_off": data.find(bytes.fromhex("aa995566")),
        "boot_off": data.find(bytes.fromhex("000000bb11220044")),
        "full_entropy_bit_per_byte": round(ent, 4),
        "zero_byte_pct": round(100 * hist[0] / n, 2),
        "ff_byte_pct": round(100 * hist[0xFF] / n, 2),
        "keyword_exact": kw,
        "dds_hit_contexts": dds_ctx,
        "freq_ascii": {f.decode(): data.count(f) for f in FREQS},
        "utf16_spi_hex": {
            "683C0350": data.count("683C0350".encode("utf-16le")),
            "83040002": data.count("83040002".encode("utf-16le")),
            "ADS62P49": data.count("ADS62P49".encode("utf-16le")),
        },
        "ipv4_ascii_count": len(re.findall(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b", data)),
        "spi_prior_words": spi,
        "window_64k_nz_pct": wins,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bin", type=Path, nargs="?", default=ROOT / "assets/firmware/20230825_s2056.bin")
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        # minimal: empty-ish buffer should run
        r = census(b"\x00" * 256 + bytes.fromhex("aa995566") + b"DDS" + b"\x00" * 16)
        assert r["keyword_exact"]["DDS"] == 1
        assert r["sync_off"] == 256
        print("self-test OK")
        return 0

    if not args.bin.is_file():
        print(f"missing {args.bin}", file=sys.stderr)
        return 2
    data = args.bin.read_bytes()
    r = census(data)
    if r["bin_sha256"] != EXPECTED_BIN:
        print(f"WARN hash != expected baseline ({r['bin_sha256']})", file=sys.stderr)
    text = json.dumps(r, indent=2, ensure_ascii=False)
    if args.json:
        args.json.write_text(text, encoding="utf-8")
        print(f"wrote {args.json}")
    else:
        # compact stdout summary
        print(f"sha256={r['bin_sha256']}")
        print(f"len={r['bin_len']} entropy={r['full_entropy_bit_per_byte']} zero%={r['zero_byte_pct']}")
        print("keywords:", {k: v for k, v in r["keyword_exact"].items() if v})
        print("freq_ascii all zero:", all(v == 0 for v in r["freq_ascii"].values()))
        print("spi_prior:", r["spi_prior_words"])
        print("dds_contexts:", r["dds_hit_contexts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
