#!/usr/bin/env python3
"""
G2 SPI 初始化序列离线译码器（被动抓包后使用）。

输入：逻辑分析仪导出的 CSV（至少含时间戳 + SCLK/MOSI/片选列），
按 ADS62P49 / DAC3283 / CDCE72010 三种帧格式拆帧，并对照
`03_architecture/FMC150_SPI靶标检查表.md` 的关键寄存器给出勾选提示。

本脚本**不连接硬件**；无板阶段仅用于：
  1. 准备好译码流水线；
  2. 用内置合成样例自检（--self-test）。

用法：
  python3 decode_spi_capture.py --self-test
  python3 decode_spi_capture.py capture.csv \\
      --sclk SCLK --mosi MOSI --cs-adc SEN --cs-dac SDENB --cs-cdce SPI_LE \\
      [--json out.json]

CSV 约定：
  - 首行为表头；时间列名可用 --time 指定（默认第一列或名含 time）。
  - 数字列：0/1 或 True/False；片选默认低有效（--cs-active high 可改）。
  - 采样应足够密（≥2.5× SCLK），脚本用边沿检测锁存，不假设固定分频。
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Frame:
    device: str
    t_start: float
    bits: list[int]
    raw_hex: str
    decoded: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 靶标提示（与 FMC150_SPI靶标检查表 对齐的最小集）
# ---------------------------------------------------------------------------

ADC_KEY_ADDR = {
    0x00: "reset/read_en",
    0x20: "low_speed",
    0x3F: "ref/standby",
    0x40: "power",
    0x41: "interface(CMOS/LVDS)",
    0x44: "clkout_phase",
    0x50: "data_format",
    0x62: "test_pattern_A",
    0x75: "test_pattern_B",
}

DAC_KEY_ADDR = {
    0x00: "CONFIG0 mixer/fifo",
    0x01: "CONFIG1 fir/interp",
    0x02: "CONFIG2",
    0x03: "CONFIG3 fifo_offset",
    0x04: "CONFIG4 coarse_gain",
    0x1F: "VERSION31",
}

CDCE_INTERNAL = {
    0x0: 0x683C034,
    0xA: 0x0FFC270,
    0xB: 0x0000828,
}
CDCE_EXTERNAL = {
    0x0: 0x683C038,
    0xA: 0x02FC07C,
    0xB: 0x00001C8,
}


def _as_bool(v: str) -> int:
    s = str(v).strip().lower()
    if s in ("1", "true", "high", "h", "yes"):
        return 1
    if s in ("0", "false", "low", "l", "no"):
        return 0
    try:
        return 1 if float(s) >= 0.5 else 0
    except ValueError as e:
        raise ValueError(f"cannot parse logic level: {v!r}") from e


def load_csv(
    path: Path,
    time_col: str | None,
    sclk: str,
    mosi: str,
    cs_map: dict[str, str],
) -> list[dict]:
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("empty CSV")
        fields = list(reader.fieldnames)
        tname = time_col
        if not tname:
            for cand in fields:
                if "time" in cand.lower() or cand.lower() in ("t", "timestamp"):
                    tname = cand
                    break
            if not tname:
                tname = fields[0]
        need = {sclk, mosi, *cs_map.values()}
        missing = need - set(fields)
        if missing:
            raise ValueError(f"CSV missing columns: {sorted(missing)}; have {fields}")
        rows = []
        for row in reader:
            item = {"t": float(row[tname]), "sclk": _as_bool(row[sclk]), "mosi": _as_bool(row[mosi])}
            for dev, col in cs_map.items():
                item[dev] = _as_bool(row[col])
            rows.append(item)
        return rows


def extract_bits_on_edge(
    rows: list[dict],
    cs_key: str,
    *,
    cs_active_low: bool,
    sample_on_falling: bool,
) -> list[tuple[float, list[int]]]:
    """片选有效期间，在指定 SCLK 边沿锁存 MOSI，返回若干帧的 bit 列表。"""
    frames: list[tuple[float, list[int]]] = []
    bits: list[int] = []
    t0: float | None = None
    prev_cs = 0
    prev_clk = rows[0]["sclk"] if rows else 0

    def cs_active(v: int) -> bool:
        return (v == 0) if cs_active_low else (v == 1)

    for r in rows:
        active = cs_active(r[cs_key])
        if active and not cs_active(prev_cs):
            bits = []
            t0 = r["t"]
        if active:
            rising = prev_clk == 0 and r["sclk"] == 1
            falling = prev_clk == 1 and r["sclk"] == 0
            if (sample_on_falling and falling) or ((not sample_on_falling) and rising):
                bits.append(r["mosi"])
        if (not active) and cs_active(prev_cs) and bits:
            frames.append((t0 if t0 is not None else r["t"], bits))
            bits = []
            t0 = None
        prev_cs = r[cs_key]
        prev_clk = r["sclk"]
    if bits and t0 is not None:
        frames.append((t0, bits))
    return frames


def bits_to_int_msb(bits: list[int]) -> int:
    v = 0
    for b in bits:
        v = (v << 1) | (b & 1)
    return v


def bits_to_int_lsb(bits: list[int]) -> int:
    v = 0
    for i, b in enumerate(bits):
        v |= (b & 1) << i
    return v


def decode_adc(t: float, bits: list[int]) -> Frame:
    fr = Frame("ADS62P49", t, bits, "")
    if len(bits) < 16:
        fr.notes.append(f"short frame ({len(bits)} bits), need 16")
        fr.raw_hex = f"0x{bits_to_int_msb(bits):X}"
        return fr
    # 取前 16；多余记 note
    use = bits[:16]
    if len(bits) > 16:
        fr.notes.append(f"extra {len(bits) - 16} bits ignored")
    word = bits_to_int_msb(use)
    fr.raw_hex = f"0x{word:04X}"
    addr, data = (word >> 8) & 0xFF, word & 0xFF
    fr.decoded = {"addr": f"0x{addr:02X}", "data": f"0x{data:02X}", "name": ADC_KEY_ADDR.get(addr, "")}
    if addr == 0x41:
        fr.notes.append("DDR LVDS" if (data & 0x80) else "parallel CMOS")
    if addr in (0x62, 0x75) and (data & 0x7):
        fr.notes.append(f"test pattern mode={data & 0x7} (H5 校准足迹?)")
    return fr


def decode_dac(t: float, bits: list[int]) -> Frame:
    fr = Frame("DAC3283", t, bits, "")
    if len(bits) < 8:
        fr.notes.append(f"short ({len(bits)} bits)")
        fr.raw_hex = f"0x{bits_to_int_msb(bits):X}"
        return fr
    instr = bits_to_int_msb(bits[:8])
    rw = (instr >> 7) & 1
    n = ((instr >> 5) & 3) + 1
    addr = instr & 0x1F
    payload_bits = bits[8 : 8 + 8 * n]
    data_bytes = []
    for i in range(0, len(payload_bits), 8):
        chunk = payload_bits[i : i + 8]
        if len(chunk) < 8:
            break
        data_bytes.append(bits_to_int_msb(chunk))
    fr.raw_hex = " ".join([f"0x{instr:02X}"] + [f"0x{b:02X}" for b in data_bytes])
    fr.decoded = {
        "rw": "R" if rw else "W",
        "addr": f"0x{addr:02X}",
        "n_bytes": n,
        "data": [f"0x{b:02X}" for b in data_bytes],
        "name": DAC_KEY_ADDR.get(addr, ""),
    }
    if addr == 0x01 and data_bytes:
        d = data_bytes[0]
        fir0, fir1 = (d >> 4) & 1, (d >> 5) & 1
        fr.notes.append(f"fir0={fir0} fir1={fir1} → interp ~{1 + fir0 + fir1*2}x(?)")
    if rw and addr == 0x1F:
        fr.notes.append("VERSION read (D2 靶标)")
    return fr


def decode_cdce(t: float, bits: list[int]) -> Frame:
    fr = Frame("CDCE72010", t, bits, "")
    if len(bits) < 32:
        fr.notes.append(f"short ({len(bits)} bits), need 32")
        fr.raw_hex = f"0x{bits_to_int_lsb(bits):X}"
        return fr
    use = bits[:32]
    if len(bits) > 32:
        fr.notes.append(f"extra {len(bits) - 32} bits ignored")
    word = bits_to_int_lsb(use)
    fr.raw_hex = f"0x{word:08X}"
    addr = word & 0xF
    data28 = (word >> 4) & 0x0FFFFFFF
    fr.decoded = {"addr": f"0x{addr:X}", "data28": f"0x{data28:07X}"}
    if addr == 0xE:
        fr.notes.append("READ command (addr field 0xE)")
    if (word & 0xFF) == 0x3F:
        fr.notes.append("!! EEPROM LOCK 0x3F — record immediately, irreversible")
    # 比对 FMC150 两列
    for label, table in (("internal", CDCE_INTERNAL), ("external", CDCE_EXTERNAL)):
        if addr in table and table[addr] == data28:
            fr.notes.append(f"matches FMC150 {label} Reg{addr:X}")
    return fr


def checklist_from_frames(frames: list[Frame]) -> dict:
    """对照靶标表 §6 给出自动勾选建议（仍需人工确认）。"""
    adc = [f for f in frames if f.device == "ADS62P49"]
    dac = [f for f in frames if f.device == "DAC3283"]
    cdce = [f for f in frames if f.device == "CDCE72010"]
    adc_addrs = set()
    for f in adc:
        a = f.decoded.get("addr")
        if a:
            adc_addrs.add(int(a, 16))
    flags = {
        "G1_adc_16bit_frames": len(adc) > 0,
        "G2_dac_instr_frames": len(dac) > 0,
        "G3_cdce_32bit_frames": len(cdce) > 0,
        "A2_adc_0x41_lvds": any(
            f.decoded.get("addr") == "0x41" and "DDR LVDS" in f.notes for f in adc
        ),
        "D1_dac_cfg1_seen": any(f.decoded.get("addr") == "0x01" for f in dac),
        "D2_dac_version_read": any("VERSION read" in n for f in dac for n in f.notes),
        "C1_cdce_writes": any(f.decoded.get("addr", "").startswith("0x") and "READ" not in "".join(f.notes) for f in cdce),
        "H5_test_pattern": any("test pattern" in n for f in adc for n in f.notes),
        "EEPROM_lock_seen": any("EEPROM LOCK" in n for f in cdce for n in f.notes),
        "adc_addr_hit_count": len(adc_addrs & set(range(0x100))),
        "adc_key_addrs_hit": sorted(hex(a) for a in adc_addrs if a in ADC_KEY_ADDR),
    }
    return flags


def run_decode(rows: list[dict], cs_active_low: bool) -> list[Frame]:
    frames: list[Frame] = []
    # ADC: 下降沿采样
    for t, bits in extract_bits_on_edge(rows, "adc", cs_active_low=cs_active_low, sample_on_falling=True):
        frames.append(decode_adc(t, bits))
    # DAC: 上升沿采样
    for t, bits in extract_bits_on_edge(rows, "dac", cs_active_low=cs_active_low, sample_on_falling=False):
        frames.append(decode_dac(t, bits))
    # CDCE: LE 低期间移位；锁存沿在参考设计中常为上升；LSB 先行与沿无关
    for t, bits in extract_bits_on_edge(rows, "cdce", cs_active_low=cs_active_low, sample_on_falling=False):
        frames.append(decode_cdce(t, bits))
    frames.sort(key=lambda f: f.t_start)
    return frames


def synthesize_self_test_csv(path: Path) -> None:
    """生成最小合成波形：ADC 写 0x4180、DAC 写 CONFIG1=0x11、CDCE Reg0 internal。"""
    rows: list[list[str]] = [["time", "SCLK", "MOSI", "SEN", "SDENB", "SPI_LE"]]

    def emit_frame(t0: float, bits_order: list[int], cs_col: int, sample_falling: bool) -> float:
        # cs_col: 3=SEN, 4=SDENB, 5=SPI_LE；空闲片选=1（高）
        t = t0

        def push(clk: int, mos: int, cs_asserted: bool) -> None:
            nonlocal t
            row = [f"{t:.9f}", str(clk), str(mos), "1", "1", "1"]
            if cs_asserted:
                row[cs_col] = "0"
            rows.append(row)
            t += 1e-8

        # 断言片选；空闲时钟：下降沿采样用高、上升沿采样用低
        idle_clk = 1 if sample_falling else 0
        push(idle_clk, 0, True)
        for b in bits_order:
            if sample_falling:
                # 置数 → 拉低采样 → 拉高准备下一位
                push(1, b, True)
                push(0, b, True)
                push(1, b, True)
            else:
                push(0, b, True)
                push(1, b, True)
                push(0, b, True)
        push(idle_clk, 0, False)
        return t + 5e-8

    t = 0.0
    adc_bits = [(0x4180 >> i) & 1 for i in range(15, -1, -1)]
    t = emit_frame(t, adc_bits, 3, True)
    dac_bits = [(0x01 >> i) & 1 for i in range(7, -1, -1)] + [(0x11 >> i) & 1 for i in range(7, -1, -1)]
    t = emit_frame(t, dac_bits, 4, False)
    word = (0x683C034 << 4) | 0x0
    cdce_bits = [(word >> i) & 1 for i in range(32)]  # LSB first 移位顺序
    t = emit_frame(t, cdce_bits, 5, False)

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)


def self_test() -> int:
    tmp = Path("/tmp/spi_self_test.csv")
    synthesize_self_test_csv(tmp)
    rows = load_csv(
        tmp,
        None,
        "SCLK",
        "MOSI",
        {"adc": "SEN", "dac": "SDENB", "cdce": "SPI_LE"},
    )
    frames = run_decode(rows, cs_active_low=True)
    print(f"self-test frames: {len(frames)}")
    for fr in frames:
        print(f"  {fr.device} {fr.raw_hex} {fr.decoded} {fr.notes}")
    flags = checklist_from_frames(frames)
    print("checklist:", json.dumps(flags, ensure_ascii=False, indent=2))
    ok = (
        flags.get("A2_adc_0x41_lvds")
        and flags.get("D1_dac_cfg1_seen")
        and any("matches FMC150 internal" in n for fr in frames for n in fr.notes)
    )
    if not ok:
        print("SELF-TEST FAILED", file=sys.stderr)
        return 1
    print("SELF-TEST OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Decode G2 SPI LA CSV for FMC150-class front-end")
    ap.add_argument("csv", nargs="?", help="logic analyzer CSV export")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sclk", default="SCLK")
    ap.add_argument("--mosi", default="MOSI")
    ap.add_argument("--cs-adc", default="SEN")
    ap.add_argument("--cs-dac", default="SDENB")
    ap.add_argument("--cs-cdce", default="SPI_LE")
    ap.add_argument("--time", dest="time_col", default=None)
    ap.add_argument("--cs-active", choices=("low", "high"), default="low")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.csv:
        ap.error("csv path required (or --self-test)")

    rows = load_csv(
        Path(args.csv),
        args.time_col,
        args.sclk,
        args.mosi,
        {"adc": args.cs_adc, "dac": args.cs_dac, "cdce": args.cs_cdce},
    )
    frames = run_decode(rows, cs_active_low=(args.cs_active == "low"))
    flags = checklist_from_frames(frames)

    print(f"decoded {len(frames)} frames from {args.csv}")
    for fr in frames:
        print(f"{fr.t_start:.9f}  {fr.device:12s}  {fr.raw_hex:20s}  {fr.decoded}  {'; '.join(fr.notes)}")
    print("\n=== checklist hints (§6) ===")
    print(json.dumps(flags, ensure_ascii=False, indent=2))

    if args.json_out:
        payload = {"frames": [asdict(f) for f in frames], "checklist": flags}
        Path(args.json_out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
