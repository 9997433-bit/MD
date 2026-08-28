#!/usr/bin/env python3
"""
G3 单音落盘分析：在已知注入频率 Fin 下估计有效样率，并做「时域 vs 已是幅度谱」粗判别。

无硬件依赖；对合成数据可 --self-test。

用法：
  python3 g3_tone_analyze.py capture.bin --fin 10e6 --fs-guess 245.76e6
  python3 g3_tone_analyze.py --self-test
"""
from __future__ import annotations

import argparse
import math
import struct
import sys
from pathlib import Path


def load_i16(path: Path, pack: str, max_n: int) -> list[float]:
    """pack: mono | ab (Conserviss-style interleaved A,B int16 LE — take channel A)."""
    raw = path.read_bytes()
    n = len(raw) // 2
    samples = list(struct.unpack(f"<{n}h", raw[: n * 2]))
    if pack == "ab":
        samples = samples[0::2]
    return [float(x) for x in samples[:max_n]]


def load_conserviss_csv(path: Path, max_n: int, channel: str = "A") -> list[float]:
    """
    Conserviss host CSV: columns include raw_code (14-bit natural) and/or signed_code.
    Matches host/analyze_adc_capture.py / write_waveform_csv conventions.
    """
    import csv

    ADC_BITS = 14
    ADC_MODULUS = 1 << ADC_BITS
    ADC_SIGN_BIT = 1 << (ADC_BITS - 1)
    out: list[float] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields = {f.lower(): f for f in (reader.fieldnames or [])}
        signed_key = fields.get("signed_code")
        raw_key = fields.get("raw_code")
        # interleaved A/B dumps may use channel_a / channel_b
        ch = channel.lower()
        ch_key = fields.get(f"channel_{ch}") or fields.get(f"adc_{ch}") or fields.get(ch)
        for row in reader:
            if signed_key and row.get(signed_key) not in (None, ""):
                out.append(float(int(row[signed_key])))
            elif ch_key and row.get(ch_key) not in (None, ""):
                raw = int(row[ch_key])
                out.append(float(raw - ADC_MODULUS if raw >= ADC_SIGN_BIT else raw))
            elif raw_key and row.get(raw_key) not in (None, ""):
                raw = int(row[raw_key])
                out.append(float(raw - ADC_MODULUS if raw >= ADC_SIGN_BIT else raw))
            else:
                continue
            if len(out) >= max_n:
                break
    return out


def load_capture(path: Path, pack: str, max_n: int) -> list[float]:
    if pack == "conserviss-csv" or path.suffix.lower() == ".csv":
        return load_conserviss_csv(path, max_n)
    return load_i16(path, pack if pack in ("mono", "ab") else "mono", max_n)


def dft_peak(x: list[float], fs: float) -> tuple[int, float, float]:
    mean = sum(x) / len(x)
    x = [v - mean for v in x]
    n = len(x)
    w = [0.5 - 0.5 * math.cos(2 * math.pi * i / max(n - 1, 1)) for i in range(n)]
    xw = [x[i] * w[i] for i in range(n)]
    half = n // 2
    peak_bin, peak_mag = 1, 0.0
    mags = [0.0] * half
    for k in range(1, half):
        re = sum(xw[i] * math.cos(2 * math.pi * k * i / n) for i in range(n))
        im = sum(-xw[i] * math.sin(2 * math.pi * k * i / n) for i in range(n))
        mag = math.hypot(re, im)
        mags[k] = mag
        if mag > peak_mag:
            peak_mag, peak_bin = mag, k
    # 第二峰
    second = sorted(((m, i) for i, m in enumerate(mags) if i != peak_bin), reverse=True)
    second_mag = second[0][0] if second else 0.0
    return peak_bin, peak_mag, second_mag


def estimate_fs(fin: float, peak_bin: int, n: int) -> float:
    if peak_bin <= 0:
        return float("nan")
    return fin * n / peak_bin


def spectrum_like_heuristic(x: list[float]) -> dict:
    """
    粗启发式（弱）：若缓冲像「已是幅度谱」，常表现为非负、低频能量占优、
    且不像正弦的过零率。不能单独升 ✅。
    """
    n = len(x)
    nonneg = sum(1 for v in x if v >= 0) / n
    zc = sum(1 for i in range(1, n) if (x[i - 1] >= 0) != (x[i] >= 0)) / n
    # 前 1/8 能量占比（把序列当谱看）
    energy = [v * v for v in x]
    tot = sum(energy) or 1.0
    head = sum(energy[: max(n // 8, 1)]) / tot
    vote_spectrum = nonneg > 0.9 and zc < 0.05 and head > 0.5
    vote_timedomain = 0.3 < nonneg < 0.7 and 0.05 < zc < 0.5
    return {
        "nonneg_frac": round(nonneg, 3),
        "zero_cross_rate": round(zc, 3),
        "head_energy_frac": round(head, 3),
        "hint": (
            "spectrum-like (weak)"
            if vote_spectrum
            else "time-domain-like (weak)"
            if vote_timedomain
            else "ambiguous"
        ),
    }


# 样钟族（与 g2_mode_infer.FAMILY 对齐；不含专利 IF/LO）
CLOCK_FAMILY_HZ = [
    30.72e6,
    40.96e6,
    61.44e6,
    81.92e6,
    122.88e6,
    163.84e6,
    245.76e6,
    491.52e6,
]

# R13b：CN117109719B 等公开 LDV 注入/监视候选（IF/LO，非样钟）
LDV_FIN_MHZ = [
    (10.0, "generic fs-estimate tone"),
    (25.0, "patent meas channel / LO square"),
    (40.0, "patent LO square / AOM-neighbour"),
    (45.0, "patent LO square"),
    (49.0, "patent LO square"),
    (50.0, "patent first meas channel"),
    (1.0, "patent low-range channel"),
    (5.0, "patent mid-low channel"),
]


def nearest_clock_family(fs: float) -> str:
    family = CLOCK_FAMILY_HZ
    if not math.isfinite(fs) or fs <= 0:
        return "n/a"
    best = min(family, key=lambda c: abs(c - fs) / c)
    err = abs(best - fs) / best
    return f"{best/1e6:.2f} MHz family (rel_err={err:.2%})"


def list_ldv_fins() -> None:
    print("R13b LDV Fin / DAC-watch candidates (NOT sample clocks):")
    print("  order  MHz     note")
    for i, (mhz, note) in enumerate(LDV_FIN_MHZ, 1):
        print(f"  {i:2d}     {mhz:5.1f}   {note}")
    print("Source: 应用域_激光测振仪.md §3b / G3G4 §2c — do not upgrade Must.")


def analyze(x: list[float], fin: float | None, fs_guess: float) -> dict:
    n = len(x)
    peak_bin, peak_mag, second_mag = dft_peak(x, fs_guess)
    f_at_guess = peak_bin * fs_guess / n
    out: dict = {
        "n": n,
        "peak_bin": peak_bin,
        "f_at_fs_guess_Hz": f_at_guess,
        "peak_to_second_ratio": (peak_mag / second_mag) if second_mag > 0 else float("inf"),
        "heuristic": spectrum_like_heuristic(x),
    }
    if fin and fin > 0:
        fs_est = estimate_fs(fin, peak_bin, n)
        out["fin_Hz"] = fin
        out["fs_estimated_Hz"] = fs_est
        out["fs_family"] = nearest_clock_family(fs_est)
        out["fin_error_at_guess"] = abs(f_at_guess - fin) / fin if fin else None
        # 若 fs_guess 正确且为时域，误差应很小；若已是谱则 bin 含义不同
        out["note"] = (
            "若 fs_estimated 落入 40.96/61.44/81.92/122.88/163.84/245.76 族且 "
            "fin_error_at_guess≪1%，支持「时域上传 + 该样率」(H2/H8；含计划 C / LDV 旁支)；"
            "若峰钉死与 Fin 无关，疑 DDC/板内谱/已解调(H-DDC/H-FFT)；"
            "Fin 优先序见 --list-ldv-fins。"
        )
    return out


def self_test() -> int:
    import csv
    import tempfile

    fs = 245.76e6
    fin = 10e6
    n = 4096
    # 生成 int16 正弦
    raw = bytearray()
    for i in range(n):
        v = int(10000 * math.sin(2 * math.pi * fin * i / fs))
        raw += struct.pack("<h", v)
    path = Path(tempfile.mkstemp(suffix=".bin")[1])
    path.write_bytes(raw)
    x = load_capture(path, "mono", n)
    r = analyze(x, fin, fs)
    print("self-test", r)
    ok = (
        r["fin_error_at_guess"] is not None
        and r["fin_error_at_guess"] < 0.02
        and "245.76" in r["fs_family"]
        and r["heuristic"]["hint"].startswith("time-domain")
    )
    # Conserviss-style A/B interleaved: A=sin, B=0
    raw_ab = bytearray()
    for i in range(n):
        a = int(10000 * math.sin(2 * math.pi * fin * i / fs))
        raw_ab += struct.pack("<hh", a, 0)
    path_ab = Path(tempfile.mkstemp(suffix="_ab.bin")[1])
    path_ab.write_bytes(raw_ab)
    r_ab = analyze(load_capture(path_ab, "ab", n), fin, fs)
    # Conserviss host CSV (14-bit raw_code)
    path_csv = Path(tempfile.mkstemp(suffix="_cons.csv")[1])
    with path_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(("index", "raw_code", "signed_code"))
        for i in range(n):
            signed = int(10000 * math.sin(2 * math.pi * fin * i / fs))
            raw_code = signed & 0x3FFF
            w.writerow((i, raw_code, signed))
    r_csv = analyze(load_capture(path_csv, "conserviss-csv", n), fin, fs)
    path.unlink(missing_ok=True)
    path_ab.unlink(missing_ok=True)
    path_csv.unlink(missing_ok=True)
    if not ok or r_ab["fin_error_at_guess"] is None or r_ab["fin_error_at_guess"] >= 0.02:
        print("SELF-TEST FAILED", r_ab, file=sys.stderr)
        return 1
    if r_csv["fin_error_at_guess"] is None or r_csv["fin_error_at_guess"] >= 0.02:
        print("SELF-TEST FAILED conserviss-csv", r_csv, file=sys.stderr)
        return 1
    print("SELF-TEST OK (incl. --pack ab + conserviss-csv)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="G3 tone capture analyzer")
    ap.add_argument("file", nargs="?", type=Path)
    ap.add_argument("--fin", type=float, help="injected tone Hz")
    ap.add_argument("--fs-guess", type=float, default=245.76e6)
    ap.add_argument(
        "--pack",
        choices=("mono", "ab", "conserviss-csv"),
        default="mono",
        help="mono int16, Conserviss A/B int16, or Conserviss host CSV (raw_code)",
    )
    ap.add_argument("--interleaved", action="store_true", help="alias for --pack ab")
    ap.add_argument("--n", type=int, default=4096)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument(
        "--list-ldv-fins",
        action="store_true",
        help="print R13b LDV Fin/DAC-watch MHz list (CN117109719B priors)",
    )
    args = ap.parse_args()
    if args.list_ldv_fins:
        list_ldv_fins()
        return 0
    if args.self_test:
        return self_test()
    if not args.file:
        ap.error("file required (or --self-test / --list-ldv-fins)")
    if not args.file.is_file():
        print(f"missing {args.file}", file=sys.stderr)
        return 2
    pack = "ab" if args.interleaved else args.pack
    if args.file.suffix.lower() == ".csv" and pack == "mono":
        pack = "conserviss-csv"
    x = load_capture(args.file, pack, args.n)
    if len(x) < args.n:
        print(f"need >= {args.n} samples, got {len(x)}", file=sys.stderr)
        return 1
    r = analyze(x, args.fin, args.fs_guess)
    for k, v in r.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
