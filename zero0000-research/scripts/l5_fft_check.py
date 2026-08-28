#!/usr/bin/env python3
"""L5 prep: offline FFT/amplitude check on captured ADC samples (no hardware)."""
from __future__ import annotations

import argparse
import math
import struct
import sys
from pathlib import Path


def load_i16(path: Path, interleaved: bool) -> list[float]:
    raw = path.read_bytes()
    n = len(raw) // 2
    samples = list(struct.unpack(f"<{n}h", raw[: n * 2]))
    if interleaved:
        # keep ch0 only for quick check
        return [float(samples[i]) for i in range(0, len(samples), 2)]
    return [float(x) for x in samples]


def main() -> int:
    ap = argparse.ArgumentParser(description="FFT sanity check for L5 ADC capture files")
    ap.add_argument("file", type=Path, help="raw int16 little-endian samples")
    ap.add_argument("--fs", type=float, default=245.76e6, help="sample rate Hz")
    ap.add_argument("--interleaved", action="store_true", help="stereo int16, use ch0")
    ap.add_argument("--n", type=int, default=4096, help="FFT length")
    args = ap.parse_args()

    if not args.file.is_file():
        print(f"missing capture: {args.file}", file=sys.stderr)
        print("Place USB/ETH recorded int16 dump here after L4/L5 capture.", file=sys.stderr)
        return 2

    x = load_i16(args.file, args.interleaved)[: args.n]
    if len(x) < args.n:
        print(f"need >= {args.n} samples, got {len(x)}", file=sys.stderr)
        return 1

    # remove DC
    mean = sum(x) / len(x)
    x = [v - mean for v in x]
    # Hann window
    n = len(x)
    w = [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
    xw = [x[i] * w[i] for i in range(n)]

    # naive DFT magnitude peak (stdlib only)
    half = n // 2
    peak_bin, peak_mag = 0, 0.0
    for k in range(1, half):
        re = sum(xw[i] * math.cos(2 * math.pi * k * i / n) for i in range(n))
        im = sum(-xw[i] * math.sin(2 * math.pi * k * i / n) for i in range(n))
        mag = math.hypot(re, im)
        if mag > peak_mag:
            peak_mag, peak_bin = mag, k

    freq = peak_bin * args.fs / n
    rms = math.sqrt(sum(v * v for v in x) / n)
    print(f"samples={n} fs={args.fs:g} peak_bin={peak_bin} f≈{freq:g} Hz rms={rms:.2f} LSB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
