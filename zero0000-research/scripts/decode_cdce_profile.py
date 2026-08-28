#!/usr/bin/env python3
"""
离线解码 CDCE72010 公开初始化剖面的输出分频（Table 8），
给出「若抓包匹配该剖面」时 C2/C3 的先验 Hz。

依据：
  - TI SCAS825 Table 8：Reg1–8 的 bits[19:13] = OUTnDIVRSEL
  - Conserviss/FMC150-VC707：code 1000000=÷2，0100000=÷1；
    Reg2 注释为 Output2 ÷2 = ADC 245.76 MHz；
    limitations：使能输出均为 ÷2 → DACCLK 亦 245.76（计划 B）

用法：
  python3 decode_cdce_profile.py
  python3 decode_cdce_profile.py --profile conserviss --vcxo 491.52e6
  python3 decode_cdce_profile.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys

# data28 values (register data field only; addr nibble stripped)
PROFILES: dict[str, dict[int, int]] = {
    "conserviss": {
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
    },
    "e2e_internal": {
        0x0: 0x683C034,
        0x1: 0x6800002,
        0x2: 0x8380000,
        0x3: 0x6800002,
        0x4: 0xE980000,
        0x5: 0x6800000,
        0x6: 0x6800000,
        0x7: 0x8380001,
        0x8: 0x6800001,
        0x9: 0x68050CC,
        0xA: 0x0FFC270,
        0xB: 0x0000828,
        0xC: 0x0000180,
    },
    "e2e_external": {
        0x0: 0x683C038,
        0x1: 0x6800002,
        0x2: 0x8380000,
        0x3: 0x6800002,
        0x4: 0xE980000,
        0x5: 0x6800000,
        0x6: 0x6800000,
        0x7: 0x8380001,
        0x8: 0x6800001,
        0x9: 0x68050CC,
        0xA: 0x02FC07C,
        0xB: 0x00001C8,
        0xC: 0x0000180,
    },
}

# Minimal Table-8 map used by FMC150-class profiles (7-bit codes as int).
# Conserviss documents 0b1000000=÷2 and 0b0100000=÷1 explicitly.
TABLE8: dict[int, int] = {
    0b0100000: 1,
    0b1000000: 2,
    0b1000001: 3,
    0b1000010: 4,
    0b1000011: 5,
    0b0000001: 6,
    0b0000010: 8,
    0b0000011: 10,
}


def outdiv_code(data28: int) -> int:
    """Extract OUTnDIVRSEL = bits[19:13] of the 28-bit data field."""
    return (data28 >> 13) & 0x7F


def decode_profile(name: str, vcxo_hz: float) -> dict:
    table = PROFILES[name]
    outs = []
    for reg in range(1, 9):
        data = table.get(reg)
        if data is None:
            continue
        code = outdiv_code(data)
        div = TABLE8.get(code)
        hz = (vcxo_hz / div) if div else None
        outs.append(
            {
                "reg": reg,
                "output": reg,  # Reg N programs Output N (N=1→Out0/1 pair; N=2→Out2 …)
                "data28": f"0x{data:07X}",
                "outdiv_code": f"0b{code:07b}",
                "divide": div,
                "hz_if_vcxo": None if hz is None else round(hz),
                "note": (
                    "Conserviss: Output2=ADC clk"
                    if name == "conserviss" and reg == 2
                    else None
                ),
            }
        )
    divs = {o["divide"] for o in outs if o["divide"]}
    plan = None
    if divs == {2}:
        plan = "B_all_div2_→ADC_and_DACCLK_245.76"
    elif 1 in divs and 2 in divs:
        plan = "mixed_div1_and_div2_→可能计划A类"
    return {
        "profile": name,
        "vcxo_hz": vcxo_hz,
        "outputs_reg1_to_8": outs,
        "plan_hint": plan,
        "g2_prior": {
            "C2_ADC_CLK_hz": 245.76e6 if 2 in divs else None,
            "C3_DACCLK_hz_if_same_as_enabled": (
                245.76e6 if plan and plan.startswith("B_") else None
            ),
            "disclaimer": "本板 Yx→ADC/DAC 布线未蜂鸣；先验仅当 SPI 剖面匹配且布线同构",
        },
    }


def self_test() -> int:
    c = decode_profile("conserviss", 491.52e6)
    # Reg2 must be ÷2
    r2 = next(o for o in c["outputs_reg1_to_8"] if o["reg"] == 2)
    if r2["divide"] != 2 or r2["hz_if_vcxo"] != 245760000:
        print("FAIL reg2", r2, file=sys.stderr)
        return 1
    if not (c["plan_hint"] or "").startswith("B_"):
        # conserviss may have some regs with unrecognized codes — check reg2+known
        known = [o for o in c["outputs_reg1_to_8"] if o["divide"] is not None]
        if not all(o["divide"] == 2 for o in known):
            print("FAIL plan", c["plan_hint"], known, file=sys.stderr)
            return 1
    print("SELF-TEST OK")
    print(json.dumps(c, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Decode CDCE72010 init profile dividers")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="conserviss")
    ap.add_argument("--vcxo", type=float, default=491.52e6)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.all:
        out = {n: decode_profile(n, args.vcxo) for n in PROFILES}
    else:
        out = decode_profile(args.profile, args.vcxo)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
