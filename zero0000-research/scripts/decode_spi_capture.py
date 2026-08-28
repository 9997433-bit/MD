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
# Conserviss/FMC150-VC707 hardware-validated profile (cdce72010_init_int_491_52MHz.coe)
# Full 32-bit words including addr nibble; data28 = word >> 4.
CDCE_CONSERVISS = {
    0x0: 0x683C035,
    0x1: 0x6800002,
    0x2: 0x8380000,
    0x3: 0x6800000,
    0x4: 0xE980000,
    0x5: 0x6800000,
    0x6: 0x6800000,
    0x7: 0x8380001,
    0x8: 0x6800009,
    0x9: 0x68050CC,
    0xA: 0x05FC270,
    0xB: 0x0000040,
    0xC: 0x0000180,
}
# RHINO thesis Plan C (ADC 61.44): Reg2 Table-8 ÷8 synthesised; Reg0/A/C Conserviss lineage.
# See decode_cdce_profile.py profile "rhino_61m44".
CDCE_RHINO_61 = {
    0x0: 0x683C035,
    0x2: 0x8304000,
    0x4: 0xE980000,
    0x7: 0x8380001,
    0xA: 0x05FC270,
    0xB: 0x0000040,
    0xC: 0x0000180,
}
DAC_CONSERVISS_CFG1 = 0x21  # FIR0=2x + twos
# Conserviss C_DAC_PRE_SYNC_CONFIG (addr → data); used for profile hit ratio only.
DAC_CONSERVISS_PRE_SYNC: dict[int, int] = {
    0x00: 0x70,
    0x01: 0x21,
    0x02: 0x00,
    0x03: 0x90,
    0x04: 0xFF,
    0x06: 0x00,
    0x07: 0x00,
    0x08: 0x00,
    0x09: 0x7A,
    0x0A: 0xB6,
    0x0B: 0xEA,
    0x0C: 0x45,
    0x0D: 0x1A,
    0x0E: 0x16,
    0x0F: 0xAA,
    0x10: 0xC6,
    0x11: 0x24,
    0x12: 0x02,
    0x13: 0x02,
    0x14: 0x00,
    0x15: 0x00,
    0x16: 0x00,
    0x17: 0x04,
    0x18: 0x83,
    0x19: 0x00,
    0x1A: 0x00,
    0x1B: 0x00,
    0x1C: 0x00,
    0x1D: 0x00,
    0x1E: 0x24,
}
# Pre-sync readback expects (CONFIG1,17,18,19,23,31) — for notes when reads appear.
DAC_CONSERVISS_PRE_VERIFY_EXPECT = {
    0x01: 0x21,
    0x11: 0x24,
    0x12: 0x02,
    0x13: 0x02,
    0x17: 0x04,
    0x1F: 0x12,
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


# Common LA export aliases (case-insensitive substring / exact).
_COL_ALIASES: dict[str, tuple[str, ...]] = {
    "time": ("time", "timestamp", "t", "time [s]", "time(s)"),
    "sclk": ("sclk", "spi_clk", "spi clk", "clock", "clk", "sck"),
    "mosi": ("mosi", "sdata", "spi_mosi", "sdio", "data", "sdi"),
    "cs_adc": ("sen", "ads_n_en", "adc_n_en", "adc_cs", "cs_adc", "ads62"),
    "cs_dac": ("sdenb", "dac_n_en", "dac_cs", "cs_dac", "dac328"),
    "cs_cdce": ("spi_le", "cdce_n_en", "cdce_cs", "cs_cdce", "le", "cdce720"),
}


def resolve_column(fields: list[str], role: str, explicit: str | None) -> str:
    """Pick CSV column for role; explicit wins if present in header."""
    if explicit and explicit in fields:
        return explicit
    if explicit and explicit not in fields:
        # allow case-insensitive exact match of user flag
        for f in fields:
            if f.lower() == explicit.lower():
                return f
    aliases = _COL_ALIASES.get(role, ())
    lowered = {f.lower().strip(): f for f in fields}
    for a in aliases:
        if a in lowered:
            return lowered[a]
    for a in aliases:
        for fl, orig in lowered.items():
            if a in fl:
                return orig
    raise ValueError(f"cannot resolve column for {role}; headers={fields}")


def load_csv(
    path: Path,
    time_col: str | None,
    sclk: str | None,
    mosi: str | None,
    cs_map: dict[str, str | None],
    *,
    auto_map: bool = False,
) -> tuple[list[dict], dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("empty CSV")
        fields = list(reader.fieldnames)
        if auto_map:
            tname = resolve_column(fields, "time", time_col)
            sclk_c = resolve_column(fields, "sclk", sclk)
            mosi_c = resolve_column(fields, "mosi", mosi)
            resolved_cs = {
                "adc": resolve_column(fields, "cs_adc", cs_map.get("adc")),
                "dac": resolve_column(fields, "cs_dac", cs_map.get("dac")),
                "cdce": resolve_column(fields, "cs_cdce", cs_map.get("cdce")),
            }
        else:
            tname = time_col
            if not tname:
                for cand in fields:
                    if "time" in cand.lower() or cand.lower() in ("t", "timestamp"):
                        tname = cand
                        break
                if not tname:
                    tname = fields[0]
            sclk_c = sclk or "SCLK"
            mosi_c = mosi or "MOSI"
            resolved_cs = {
                "adc": cs_map.get("adc") or "SEN",
                "dac": cs_map.get("dac") or "SDENB",
                "cdce": cs_map.get("cdce") or "SPI_LE",
            }
            need = {sclk_c, mosi_c, *resolved_cs.values()}
            missing = need - set(fields)
            if missing:
                raise ValueError(
                    f"CSV missing columns: {sorted(missing)}; have {fields}. "
                    f"Try --auto-map"
                )
        mapping = {"time": tname, "sclk": sclk_c, "mosi": mosi_c, **{f"cs_{k}": v for k, v in resolved_cs.items()}}
        rows = []
        for row in reader:
            item = {
                "t": float(row[tname]),
                "sclk": _as_bool(row[sclk_c]),
                "mosi": _as_bool(row[mosi_c]),
            }
            for dev, col in resolved_cs.items():
                item[dev] = _as_bool(row[col])
            rows.append(item)
        return rows, mapping


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
        if d == DAC_CONSERVISS_CFG1:
            fr.notes.append("matches Conserviss FMC150-VC707 CONFIG1 (2x+twos)")
    if (not rw) and addr in DAC_CONSERVISS_PRE_SYNC and data_bytes:
        if data_bytes[0] == DAC_CONSERVISS_PRE_SYNC[addr]:
            fr.notes.append(f"matches Conserviss pre-sync CONFIG{addr}")
    if rw and addr in DAC_CONSERVISS_PRE_VERIFY_EXPECT and data_bytes:
        exp = DAC_CONSERVISS_PRE_VERIFY_EXPECT[addr]
        got = data_bytes[0]
        if got == exp:
            fr.notes.append(f"Conserviss pre-verify CONFIG{addr}=0x{got:02X} ok")
        else:
            fr.notes.append(f"pre-verify CONFIG{addr}=0x{got:02X}≠0x{exp:02X}")
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
    # 比对 FMC150 两列 + Conserviss VC707 硬件表
    for label, table in (
        ("internal", CDCE_INTERNAL),
        ("external", CDCE_EXTERNAL),
        ("conserviss", CDCE_CONSERVISS),
        ("rhino_61m44", CDCE_RHINO_61),
    ):
        if addr in table and table[addr] == data28:
            fr.notes.append(f"matches FMC150 {label} Reg{addr:X}")
    return fr


def checklist_from_frames(frames: list[Frame]) -> dict:
    """对照靶标表 §6 给出自动勾选建议（仍需人工确认）。"""
    adc = [f for f in frames if f.device == "ADS62P49"]
    dac = [f for f in frames if f.device == "DAC3283"]
    cdce = [f for f in frames if f.device == "CDCE72010"]
    adc_addrs = set()
    adc_words: set[tuple[int, int]] = set()
    for f in adc:
        a = f.decoded.get("addr")
        d = f.decoded.get("data")
        if a:
            ai = int(a, 16)
            adc_addrs.add(ai)
            if d:
                adc_words.add((ai, int(d, 16)))
    cdce_by_addr: dict[int, int] = {}
    for f in cdce:
        if "READ" in "".join(f.notes):
            continue
        a = f.decoded.get("addr")
        d = f.decoded.get("data28")
        if a and d:
            cdce_by_addr[int(a, 16)] = int(d, 16)

    def profile_hits(table: dict[int, int]) -> tuple[int, int, list[str]]:
        hit = 0
        detail = []
        for addr, expect in table.items():
            got = cdce_by_addr.get(addr)
            if got == expect:
                hit += 1
                detail.append(f"Reg{addr:X}=ok")
            elif got is not None:
                detail.append(f"Reg{addr:X}=0x{got:07X}≠0x{expect:07X}")
        return hit, len(table), detail

    c_hit, c_n, c_detail = profile_hits(CDCE_CONSERVISS)
    i_hit, i_n, _ = profile_hits(CDCE_INTERNAL)
    e_hit, e_n, _ = profile_hits(CDCE_EXTERNAL)
    r_hit, r_n, r_detail = profile_hits(CDCE_RHINO_61)

    dac_cfg1 = None
    dac_writes: dict[int, int] = {}
    for f in dac:
        if f.decoded.get("rw") == "R":
            continue
        a = f.decoded.get("addr")
        dlist = f.decoded.get("data") or []
        if not a or not dlist:
            continue
        try:
            ai, di = int(a, 16), int(dlist[0], 16)
        except (TypeError, ValueError, IndexError):
            continue
        dac_writes[ai] = di  # last write wins
        if ai == 0x01 and dac_cfg1 is None:
            dac_cfg1 = di

    dac_pre_hit = 0
    dac_pre_detail: list[str] = []
    for addr, expect in DAC_CONSERVISS_PRE_SYNC.items():
        got = dac_writes.get(addr)
        if got == expect:
            dac_pre_hit += 1
        elif got is not None:
            dac_pre_detail.append(f"C{addr:02X}=0x{got:02X}≠0x{expect:02X}")

    flags = {
        "G1_adc_16bit_frames": len(adc) > 0,
        "G2_dac_instr_frames": len(dac) > 0,
        "G3_cdce_32bit_frames": len(cdce) > 0,
        "A2_adc_0x41_lvds": any(
            f.decoded.get("addr") == "0x41" and "DDR LVDS" in f.notes for f in adc
        ),
        "A_adc_0x50_twos": (0x50, 0x04) in adc_words,
        "D1_dac_cfg1_seen": any(f.decoded.get("addr") == "0x01" for f in dac),
        "D2_dac_version_read": any("VERSION read" in n for f in dac for n in f.notes),
        "C1_cdce_writes": any(
            f.decoded.get("addr", "").startswith("0x") and "READ" not in "".join(f.notes)
            for f in cdce
        ),
        "H5_test_pattern": any("test pattern" in n for f in adc for n in f.notes),
        "EEPROM_lock_seen": any("EEPROM LOCK" in n for f in cdce for n in f.notes),
        "adc_addr_hit_count": len(adc_addrs & set(range(0x100))),
        "adc_key_addrs_hit": sorted(hex(a) for a in adc_addrs if a in ADC_KEY_ADDR),
        "conserviss_cdce_reg_hits": c_hit,
        "conserviss_cdce_reg_total": c_n,
        "conserviss_cdce_match_ratio": round(c_hit / c_n, 3) if c_n else 0.0,
        "conserviss_cdce_detail": c_detail,
        "rhino_61m44_cdce_reg_hits": r_hit,
        "rhino_61m44_cdce_reg_total": r_n,
        "rhino_61m44_cdce_match_ratio": round(r_hit / r_n, 3) if r_n else 0.0,
        "rhino_61m44_cdce_detail": r_detail,
        "e2e_internal_cdce_hits": i_hit,
        "e2e_internal_cdce_total": i_n,
        "e2e_external_cdce_hits": e_hit,
        "e2e_external_cdce_total": e_n,
        "conserviss_dac_cfg1": dac_cfg1 == DAC_CONSERVISS_CFG1,
        "dac_cfg1_value": None if dac_cfg1 is None else f"0x{dac_cfg1:02X}",
        "conserviss_dac_pre_sync_hits": dac_pre_hit,
        "conserviss_dac_pre_sync_total": len(DAC_CONSERVISS_PRE_SYNC),
        "conserviss_dac_pre_sync_ratio": round(dac_pre_hit / len(DAC_CONSERVISS_PRE_SYNC), 3),
        "conserviss_dac_pre_sync_mismatches": dac_pre_detail[:12],
        "best_cdce_profile": _best_cdce_profile(
            c_hit, c_n, r_hit, r_n, i_hit, e_hit, cdce_by_addr
        ),
    }
    return flags


def _best_cdce_profile(
    c_hit: int,
    c_n: int,
    r_hit: int,
    r_n: int,
    i_hit: int,
    e_hit: int,
    cdce_by_addr: dict[int, int],
) -> str:
    """Pick best CDCE init profile.

    RHINO Plan C is only eligible when Reg2 is the ÷8 word (0x8304000).
    Shared Reg0/A with Conserviss must not let a partial rhino ratio win.
    """
    reg2 = cdce_by_addr.get(0x2)
    if reg2 == 0x8304000 and r_hit > 0:
        return "rhino_61m44"
    # If Reg2 is Conserviss/E2E ÷2 style, do not score rhino at all.
    r_score_hits = r_hit if reg2 == 0x8304000 else 0
    scores = [
        ("conserviss", (c_hit / c_n if c_n else 0.0, c_hit)),
        (
            "rhino_61m44",
            (r_score_hits / r_n if r_n and r_score_hits else 0.0, r_score_hits),
        ),
        (
            "e2e_internal",
            (i_hit / len(CDCE_INTERNAL), i_hit) if CDCE_INTERNAL else (0.0, 0),
        ),
        (
            "e2e_external",
            (e_hit / len(CDCE_EXTERNAL), e_hit) if CDCE_EXTERNAL else (0.0, 0),
        ),
    ]
    name, (_ratio, hits) = max(scores, key=lambda x: (x[1][0], x[1][1]))
    return name if hits > 0 else "none"


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
    _write_spi_csv(path, _synth_frames_e2e_min())


def synthesize_conserviss_min_csv(path: Path) -> None:
    """Conserviss 最小足迹：ADC 4180/5004、DAC CFG1=0x21、CDCE Reg0+2+A。"""
    _write_spi_csv(path, _synth_frames_conserviss_min())


def synthesize_rhino_min_csv(path: Path) -> None:
    """RHINO 计划 C 最小足迹：CDCE Reg2=÷8 + Reg7=÷2。"""
    _write_spi_csv(path, _synth_frames_rhino_min())


def _write_spi_csv(path: Path, frame_specs: list[tuple[list[int], int, bool]]) -> None:
    rows: list[list[str]] = [["time", "SCLK", "MOSI", "SEN", "SDENB", "SPI_LE"]]

    def emit_frame(t0: float, bits_order: list[int], cs_col: int, sample_falling: bool) -> float:
        t = t0

        def push(clk: int, mos: int, cs_asserted: bool) -> None:
            nonlocal t
            row = [f"{t:.9f}", str(clk), str(mos), "1", "1", "1"]
            if cs_asserted:
                row[cs_col] = "0"
            rows.append(row)
            t += 1e-8

        idle_clk = 1 if sample_falling else 0
        push(idle_clk, 0, True)
        for b in bits_order:
            if sample_falling:
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
    for bits, cs_col, falling in frame_specs:
        t = emit_frame(t, bits, cs_col, falling)

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)


def _msb_bits(val: int, n: int) -> list[int]:
    return [(val >> i) & 1 for i in range(n - 1, -1, -1)]


def _cdce_lsb_bits(data28: int, addr: int) -> list[int]:
    word = ((data28 & 0x0FFFFFFF) << 4) | (addr & 0xF)
    return [(word >> i) & 1 for i in range(32)]


def _synth_frames_e2e_min() -> list[tuple[list[int], int, bool]]:
    adc = _msb_bits(0x4180, 16)
    dac = _msb_bits(0x01, 8) + _msb_bits(0x11, 8)
    cdce = _cdce_lsb_bits(0x683C034, 0)
    return [(adc, 3, True), (dac, 4, False), (cdce, 5, False)]


def _synth_frames_conserviss_min() -> list[tuple[list[int], int, bool]]:
    frames: list[tuple[list[int], int, bool]] = [
        (_msb_bits(0x4180, 16), 3, True),
        (_msb_bits(0x5004, 16), 3, True),
        (_msb_bits(0x01, 8) + _msb_bits(0x21, 8), 4, False),
    ]
    # Reg0, Reg2 (ADC clk ÷2), RegA — enough for conserviss best_cdce_profile
    for addr, data28 in ((0, 0x683C035), (2, 0x8380000), (0xA, 0x05FC270)):
        frames.append((_cdce_lsb_bits(data28, addr), 5, False))
    return frames


def _synth_frames_rhino_min() -> list[tuple[list[int], int, bool]]:
    frames: list[tuple[list[int], int, bool]] = [
        (_msb_bits(0x4180, 16), 3, True),
        (_msb_bits(0x5004, 16), 3, True),
        (_msb_bits(0x01, 8) + _msb_bits(0x21, 8), 4, False),
    ]
    for addr, data28 in (
        (0, 0x683C035),
        (2, 0x8304000),
        (7, 0x8380001),
        (0xA, 0x05FC270),
    ):
        frames.append((_cdce_lsb_bits(data28, addr), 5, False))
    return frames


def self_test() -> int:
    tmp = Path("/tmp/spi_self_test.csv")
    synthesize_self_test_csv(tmp)
    rows, mapping = load_csv(
        tmp,
        None,
        "SCLK",
        "MOSI",
        {"adc": "SEN", "dac": "SDENB", "cdce": "SPI_LE"},
        auto_map=False,
    )
    print(f"self-test column map: {mapping}")
    frames = run_decode(rows, cs_active_low=True)
    print(f"self-test frames: {len(frames)}")
    for fr in frames:
        print(f"  {fr.device} {fr.raw_hex} {fr.decoded} {fr.notes}")
    flags = checklist_from_frames(frames)
    print("checklist:", json.dumps(flags, ensure_ascii=False, indent=2))
    # auto-map path on renamed headers
    tmp2 = Path("/tmp/spi_self_test_aliases.csv")
    text = tmp.read_text(encoding="utf-8")
    text = (
        text.replace("time", "Time [s]", 1)
        .replace("SCLK", "SPI_CLK", 1)
        .replace("MOSI", "SDATA", 1)
        .replace("SEN", "ADC_CS", 1)
        .replace("SDENB", "DAC_CS", 1)
        .replace("SPI_LE", "CDCE_CS", 1)
    )
    tmp2.write_text(text, encoding="utf-8")
    rows2, map2 = load_csv(tmp2, None, None, None, {"adc": None, "dac": None, "cdce": None}, auto_map=True)
    flags2 = checklist_from_frames(run_decode(rows2, True))
    ok = (
        flags.get("A2_adc_0x41_lvds")
        and flags.get("D1_dac_cfg1_seen")
        and any("matches FMC150 internal" in n for fr in frames for n in fr.notes)
        and flags2.get("A2_adc_0x41_lvds")
    )
    if not ok:
        print("SELF-TEST FAILED", map2, flags2, file=sys.stderr)
        return 1
    # Conserviss min footprint
    tmp3 = Path("/tmp/spi_conserviss_min.csv")
    synthesize_conserviss_min_csv(tmp3)
    flags3 = checklist_from_frames(
        run_decode(
            load_csv(
                tmp3,
                None,
                "SCLK",
                "MOSI",
                {"adc": "SEN", "dac": "SDENB", "cdce": "SPI_LE"},
                auto_map=False,
            )[0],
            True,
        )
    )
    if (
        flags3.get("best_cdce_profile") != "conserviss"
        or not flags3.get("conserviss_dac_cfg1")
        or not flags3.get("A_adc_0x50_twos")
    ):
        print("SELF-TEST FAILED conserviss min", flags3, file=sys.stderr)
        return 1
    tmp4 = Path("/tmp/spi_rhino_min.csv")
    synthesize_rhino_min_csv(tmp4)
    flags4 = checklist_from_frames(
        run_decode(
            load_csv(
                tmp4,
                None,
                "SCLK",
                "MOSI",
                {"adc": "SEN", "dac": "SDENB", "cdce": "SPI_LE"},
                auto_map=False,
            )[0],
            True,
        )
    )
    if flags4.get("best_cdce_profile") != "rhino_61m44":
        print("SELF-TEST FAILED rhino min", flags4, file=sys.stderr)
        return 1
    print("SELF-TEST OK (incl. --auto-map aliases + conserviss/rhino min)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Decode G2 SPI LA CSV for FMC150-class front-end")
    ap.add_argument("csv", nargs="?", help="logic analyzer CSV export")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sclk", default=None, help="default SCLK; with --auto-map optional")
    ap.add_argument("--mosi", default=None)
    ap.add_argument("--cs-adc", default=None)
    ap.add_argument("--cs-dac", default=None)
    ap.add_argument("--cs-cdce", default=None)
    ap.add_argument("--time", dest="time_col", default=None)
    ap.add_argument("--cs-active", choices=("low", "high"), default="low")
    ap.add_argument("--auto-map", action="store_true", help="resolve Saleae/PulseView-style column aliases")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--write-example", type=Path, help="write synthetic E2E-min example CSV and exit")
    ap.add_argument(
        "--write-conserviss-example",
        type=Path,
        help="write synthetic Conserviss-min example CSV and exit",
    )
    ap.add_argument(
        "--write-rhino-example",
        type=Path,
        help="write synthetic RHINO Plan-C min example CSV and exit",
    )
    args = ap.parse_args()

    if args.write_example:
        synthesize_self_test_csv(args.write_example)
        print(f"wrote example {args.write_example}")
        return 0
    if args.write_conserviss_example:
        synthesize_conserviss_min_csv(args.write_conserviss_example)
        print(f"wrote conserviss example {args.write_conserviss_example}")
        return 0
    if args.write_rhino_example:
        synthesize_rhino_min_csv(args.write_rhino_example)
        print(f"wrote rhino example {args.write_rhino_example}")
        return 0
    if args.self_test:
        return self_test()
    if not args.csv:
        ap.error("csv path required (or --self-test)")

    auto = args.auto_map or not all([args.sclk, args.mosi, args.cs_adc, args.cs_dac, args.cs_cdce])
    # backward compatible defaults when not auto
    sclk = args.sclk or ("SCLK" if not auto else None)
    mosi = args.mosi or ("MOSI" if not auto else None)
    cs_adc = args.cs_adc or ("SEN" if not auto else None)
    cs_dac = args.cs_dac or ("SDENB" if not auto else None)
    cs_cdce = args.cs_cdce or ("SPI_LE" if not auto else None)

    rows, mapping = load_csv(
        Path(args.csv),
        args.time_col,
        sclk,
        mosi,
        {"adc": cs_adc, "dac": cs_dac, "cdce": cs_cdce},
        auto_map=auto,
    )
    print(f"column map: {mapping}")
    frames = run_decode(rows, cs_active_low=(args.cs_active == "low"))
    flags = checklist_from_frames(frames)

    print(f"decoded {len(frames)} frames from {args.csv}")
    for fr in frames:
        print(f"{fr.t_start:.9f}  {fr.device:12s}  {fr.raw_hex:20s}  {fr.decoded}  {'; '.join(fr.notes)}")
    print("\n=== checklist hints (§6) ===")
    print(json.dumps(flags, ensure_ascii=False, indent=2))

    if args.json_out:
        payload = {"frames": [asdict(f) for f in frames], "checklist": flags, "column_map": mapping}
        Path(args.json_out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
