#!/usr/bin/env python3
"""
G2 结果 → P1.3/P1.4/P1.5 等级建议（离线）。

输入：
  --clocks clocks.json   [{"id":"C2","hz":245.76e6}, ...]
  --spi spi_decode.json  decode_spi_capture.py 的 --json 输出

无输入时打印 schema 与示例；--self-test 用合成数据跑通。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FAMILY = {
    "122.88e6": 122.88e6,
    "245.76e6": 245.76e6,
    "491.52e6": 491.52e6,
}


def near_family(hz: float, tol: float = 0.01) -> str | None:
    for name, f in FAMILY.items():
        if abs(hz - f) / f <= tol:
            return name
    return None


def infer_clocks(clocks: list[dict]) -> dict:
    by_id = {c["id"]: c.get("hz") for c in clocks if "id" in c and c.get("hz")}
    notes = []
    p13 = "❓"
    adc = by_id.get("C2") or by_id.get("ADC_CLK")
    dac = by_id.get("C3") or by_id.get("DACCLK")
    data = by_id.get("C6") or by_id.get("DATACLK")
    adc_f = near_family(adc) if adc else None
    dac_f = near_family(dac) if dac else None
    if adc and adc_f:
        notes.append(f"ADC clk ≈ {adc_f}")
    elif adc:
        notes.append(f"ADC clk={adc} Hz 不在 122.88/245.76/491.52 族（tol 1%）")
    if dac and dac_f:
        notes.append(f"DACCLK ≈ {dac_f}")
    elif dac:
        notes.append(f"DACCLK={dac} Hz 不在族内")
    # 命题要求测得 ADC 与 DAC；单侧落入族 → 强 🔶；双侧 → ✅
    if adc and dac:
        if adc_f and dac_f:
            p13 = "✅"
        elif adc_f or dac_f:
            p13 = "🔶"
            notes.append("仅一侧落入族或另一侧偏离 → 强 🔶，未满 ✅")
        else:
            p13 = "🔶"
            notes.append("双侧测得但均偏离先验族 → 🔶（需复核探点）")
        ratio = dac / adc if adc else None
        if ratio:
            notes.append(f"DACCLK/ADC ≈ {ratio:.3f}")
    elif adc or dac:
        if adc_f or dac_f:
            p13 = "🔶"
            notes.append("仅测得一侧且落入族 → 强 🔶；补另一侧可冲 ✅")
        else:
            p13 = "🔶"
            notes.append("仅测得一侧且偏离族 → 🔶")
    interp = None
    if dac and data and data > 0:
        interp = round(dac / data)
        notes.append(f"DACCLK/DATACLK ≈ {dac/data:.3f} → interp hint {interp}x")
    return {
        "P1.3_suggested": p13,
        "interp_hint": interp,
        "notes": notes,
        "H8": (
            "支持"
            if adc
            and dac
            and adc_f in ("122.88e6", "245.76e6")
            and dac_f == "491.52e6"
            else ("弱支持（单侧）" if (adc_f or dac_f) and not (adc and dac) else "未触及/弱")
        ),
    }


def infer_spi(checklist: dict, frames: list | None = None) -> dict:
    notes = []
    p14 = "❓"
    p15 = "❓"
    if checklist.get("A2_adc_0x41_lvds"):
        notes.append("ADC 0x41 DDR LVDS 写见到 → P1.2/P1.4 强")
        p14 = "✅"
    if checklist.get("D1_dac_cfg1_seen"):
        notes.append("DAC CONFIG1 见到 → 可读插值位")
        if p14 == "❓":
            p14 = "🔶"
    if checklist.get("C1_cdce_writes"):
        notes.append("CDCE 写序列存在 → 非纯 EEPROM 沉默")
        p15 = "🔶（倾向位流内 SPI 主控；需对照「仅上电无主机」实验定 ✅）"
    elif checklist.get("G3_cdce_32bit_frames") is False and checklist.get("G1_adc_16bit_frames") is False:
        notes.append("三片均无帧 → 或未抓到，或全 EEPROM/主机未接")
    if checklist.get("H5_test_pattern"):
        notes.append("ADC 测试图样写入 → H5 支持")
    if checklist.get("EEPROM_lock_seen"):
        notes.append("!! EEPROM lock 0x3F 出现")
    return {"P1.4_suggested": p14, "P1.5_suggested": p15, "notes": notes}


def self_test() -> int:
    clocks = [{"id": "C2", "hz": 245.76e6}, {"id": "C3", "hz": 491.52e6}, {"id": "C6", "hz": 245.76e6}]
    checklist = {
        "A2_adc_0x41_lvds": True,
        "D1_dac_cfg1_seen": True,
        "C1_cdce_writes": True,
        "H5_test_pattern": False,
        "EEPROM_lock_seen": False,
    }
    c = infer_clocks(clocks)
    s = infer_spi(checklist)
    print(json.dumps({"clocks": c, "spi": s}, ensure_ascii=False, indent=2))
    ok = c["P1.3_suggested"] == "✅" and s["P1.4_suggested"] == "✅" and c["interp_hint"] == 2
    # single-sided clock → 强 🔶
    c1 = infer_clocks([{"id": "C2", "hz": 245.76e6}])
    if c1["P1.3_suggested"] != "🔶":
        print("SELF-TEST FAILED single-sided", c1, file=sys.stderr)
        return 1
    if not ok:
        print("SELF-TEST FAILED", file=sys.stderr)
        return 1
    print("SELF-TEST OK (incl. single-sided → 🔶)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clocks", type=Path)
    ap.add_argument("--spi", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.clocks and not args.spi:
        print(
            json.dumps(
                {
                    "clocks_schema": [{"id": "C2", "hz": 245.76e6, "note": "ADC CLKP"}],
                    "spi_schema": "decode_spi_capture.py --json output",
                },
                indent=2,
            )
        )
        return 0
    out: dict = {}
    if args.clocks:
        out["clocks"] = infer_clocks(json.loads(args.clocks.read_text()))
    if args.spi:
        blob = json.loads(args.spi.read_text())
        out["spi"] = infer_spi(blob.get("checklist", blob), blob.get("frames"))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
