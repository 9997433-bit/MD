#!/usr/bin/env python3
"""
在 MCS/BIN 镜像中搜索 FMC150 生态公开 SPI 配置常量。

目的（G1 加深 / 无板可做）：
  若位流 BRAM/初始化 ROM 以明文字节存放 CDCE/ADC/DAC 写表，
  可在镜像中命中已知 28/32-bit 或 16-bit 帧；命中 ≠ 本板已启用该配置，
  但「完全未命中」可加强「配置表经压缩/混淆/运行时生成」的先验。

用法：
  python3 search_spi_constants.py [镜像路径] [--json out.json]

默认从 zero0000-research/assets/firmware/ 自动定位 .bin 或 .mcs。
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 镜像加载（与 search_net_constants.py 同构）
# ---------------------------------------------------------------------------


def load_mcs(path: Path) -> bytearray:
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
                segments[upper + addr] = payload
    if not segments:
        return bytearray()
    max_addr = max(base + len(p) for base, p in segments.items())
    data = bytearray(b"\xff" * max_addr)
    for base, payload in segments.items():
        data[base : base + len(payload)] = payload
    return data


def load_image(path: Path) -> bytearray:
    if path.suffix.lower() == ".mcs":
        return load_mcs(path)
    return bytearray(path.read_bytes())


def autolocate() -> Path | None:
    here = Path(__file__).resolve().parent
    fw = here.parent / "assets" / "firmware"
    for name in ("20230825_s2056.bin", "20230825_s2056.mcs"):
        p = fw / name
        if p.exists():
            return p
    cands = list(fw.glob("*.bin")) + list(fw.glob("*.mcs"))
    return cands[0] if cands else None


# ---------------------------------------------------------------------------
# 靶标常量（来源：FMC150_SPI靶标检查表.md §5.3 / §3 / §4；TI E2E / SCAA090）
# ---------------------------------------------------------------------------

# CDCE72010：公开表给的是 28-bit 数据场；完整 SPI 字 = (data28 << 4) | addr4
CDCE_INTERNAL_28 = {
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
}

CDCE_EXTERNAL_28 = {
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
}

# TI 出厂 EEPROM 默认（SCAA090，含地址半字节的 32-bit 首字示例）
CDCE_SCAA090_REG0_32 = 0x002C0040

# ADS62P49：16-bit 帧 = addr8 | data8；高价值靶标
ADC_FRAMES = {
    "soft_reset_0x00": 0x0001,  # 常见：addr0 + read-enable 等变体也搜
    "reset_only_0x00_80": 0x0080,  # soft reset bit D7（若写）
    "ddr_lvds_0x41_80": 0x4180,  # D7=1 DDR LVDS —— 最强判据
    "ddr_lvds_0x41_00": 0x4100,  # CMOS 对照（期望不应为主配置）
    "low_speed_off_0x20": 0x2000,
    "power_normal_0x40": 0x4008,
    "test_ramp_0x62": 0x6204,
    "test_toggle_0x62": 0x6203,
    "test_off_0x62": 0x6200,
    "test_ramp_0x75": 0x7504,
}

# DAC3283：指令字节(写, N=0, addr) + 数据；搜 16-bit 组合
# CONFIG1 默认 0x11；fir0_ena=bit4 → 2x 插值时常为 0x11 或带 fir 的变体
DAC_FRAMES = {
    "cfg0_write_0x00": 0x0070,  # instr=0x00 write addr0, data default 0x70
    "cfg1_write_0x01_11": 0x0111,  # fir0/fir1 默认
    "cfg1_fir0_only": 0x0110,  # 可能的 2x 变体
    "version_read_instr": 0x9F,  # 单字节读指令 R=1,N=0,A=0x1F（搜字节）
}


def find_all(hay: bytes, needle: bytes, limit: int = 32) -> list[int]:
    out: list[int] = []
    start = 0
    while len(out) < limit:
        i = hay.find(needle, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out


def u32_patterns(word: int) -> list[tuple[str, bytes]]:
    """大端/小端完整字 + 28-bit 数据场单独搜索。"""
    be = struct.pack(">I", word & 0xFFFFFFFF)
    le = struct.pack("<I", word & 0xFFFFFFFF)
    return [("BE32", be), ("LE32", le)]


def search_cdce(data: bytes) -> dict:
    results: dict = {"internal_full32": [], "external_full32": [], "data28_only": [], "scaa090": []}

    def pack_full(data28: int, addr: int) -> int:
        return ((data28 & 0x0FFFFFFF) << 4) | (addr & 0xF)

    for label, table in (("internal", CDCE_INTERNAL_28), ("external", CDCE_EXTERNAL_28)):
        bucket = results[f"{label}_full32"]
        for addr, d28 in table.items():
            full = pack_full(d28, addr)
            for endian, pat in u32_patterns(full):
                hits = find_all(data, pat)
                if hits:
                    bucket.append(
                        {
                            "reg": addr,
                            "data28": f"0x{d28:07X}",
                            "full32": f"0x{full:08X}",
                            "endian": endian,
                            "count": len(hits),
                            "offsets": [f"0x{h:X}" for h in hits[:8]],
                        }
                    )
            # 仅 28-bit 数据场（7 半字节不好对齐；用 4 字节右对齐 0x0XXXXXXX）
            for endian, pat in u32_patterns(d28):
                hits = find_all(data, pat)
                if hits:
                    results["data28_only"].append(
                        {
                            "scheme": label,
                            "reg": addr,
                            "data28": f"0x{d28:07X}",
                            "as32": f"0x{d28:08X}",
                            "endian": endian,
                            "count": len(hits),
                            "offsets": [f"0x{h:X}" for h in hits[:8]],
                        }
                    )

    for endian, pat in u32_patterns(CDCE_SCAA090_REG0_32):
        hits = find_all(data, pat)
        if hits:
            results["scaa090"].append(
                {
                    "word": f"0x{CDCE_SCAA090_REG0_32:08X}",
                    "endian": endian,
                    "count": len(hits),
                    "offsets": [f"0x{h:X}" for h in hits[:8]],
                }
            )
    return results


def search_adc(data: bytes) -> list[dict]:
    out: list[dict] = []
    for name, frame in ADC_FRAMES.items():
        be = struct.pack(">H", frame)
        le = struct.pack("<H", frame)
        for endian, pat in (("BE16", be), ("LE16", le)):
            hits = find_all(data, pat, limit=64)
            # 16-bit 帧噪声极大；仅报告命中次数与样例，由人判读
            if hits:
                out.append(
                    {
                        "name": name,
                        "frame": f"0x{frame:04X}",
                        "endian": endian,
                        "count": len(hits),
                        "offsets_sample": [f"0x{h:X}" for h in hits[:6]],
                    }
                )
    return out


def search_dac(data: bytes) -> list[dict]:
    out: list[dict] = []
    for name, val in DAC_FRAMES.items():
        if val <= 0xFF:
            pat = bytes([val])
            hits = find_all(data, pat, limit=8)
            # 单字节几乎无信息；跳过纯字节泛滥报告
            continue
        be = struct.pack(">H", val)
        le = struct.pack("<H", val)
        for endian, pat in (("BE16", be), ("LE16", le)):
            hits = find_all(data, pat, limit=64)
            if hits:
                out.append(
                    {
                        "name": name,
                        "frame": f"0x{val:04X}",
                        "endian": endian,
                        "count": len(hits),
                        "offsets_sample": [f"0x{h:X}" for h in hits[:6]],
                    }
                )
    # 读版本指令字节密度（仅作旁证）
    ver_hits = find_all(data, b"\x9f", limit=8)
    out.append(
        {
            "name": "version_read_instr_0x9F_byte",
            "frame": "0x9F",
            "endian": "byte",
            "count": len(ver_hits) if ver_hits else data.count(b"\x9f"),
            "note": "单字节命中噪声极高，不可单独作结论",
            "offsets_sample": [f"0x{h:X}" for h in ver_hits[:6]],
        }
    )
    return out


def score_summary(cdce: dict, adc: list, dac: list) -> dict:
    """给出可写入文档的一句话结论材料。"""
    int_hits = len(cdce["internal_full32"])
    ext_hits = len(cdce["external_full32"])
    scaa = len(cdce["scaa090"])
    d28 = len(cdce["data28_only"])

    # ADC：0x4180 是最强靶标
    adc_lvds = [x for x in adc if x["name"] == "ddr_lvds_0x41_80"]
    adc_lvds_n = sum(x["count"] for x in adc_lvds)

    return {
        "cdce_internal_full32_regs_hit": int_hits,
        "cdce_external_full32_regs_hit": ext_hits,
        "cdce_scaa090_hit": scaa > 0,
        "cdce_data28_only_rows": d28,
        "adc_0x4180_hit_count_sum": adc_lvds_n,
        "interpretation_zh": (
            "若 CDCE full32 / SCAA090 / ADC 0x4180 均无可信成簇命中，"
            "则位流内不以明文 FMC150 写表形式存放初始化 ROM；"
            "这与『配置经状态机即时拼帧 / 表经压缩 / 或依赖 CDCE EEPROM 自举』相容，"
            "但不能排除 SPI 主控存在——G2 嗅探仍是唯一裁决。"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Search MCS/BIN for FMC150 SPI constants")
    ap.add_argument("image", nargs="?", help="path to .mcs or .bin")
    ap.add_argument("--json", dest="json_out", help="write full JSON report")
    args = ap.parse_args()

    path = Path(args.image) if args.image else autolocate()
    if not path or not path.exists():
        print("ERROR: firmware image not found", file=sys.stderr)
        return 1

    print(f"loading {path} …", flush=True)
    data = load_image(path)
    print(f"image size: {len(data)} bytes (0x{len(data):X})")

    cdce = search_cdce(data)
    adc = search_adc(data)
    dac = search_dac(data)
    summary = score_summary(cdce, adc, dac)

    report = {
        "image": str(path),
        "size": len(data),
        "cdce": cdce,
        "adc_frames": adc,
        "dac_frames": dac,
        "summary": summary,
    }

    print("\n=== CDCE full32 (internal) hits ===")
    if not cdce["internal_full32"]:
        print("  (none)")
    for row in cdce["internal_full32"]:
        print(f"  reg{row['reg']:X} {row['full32']} {row['endian']} ×{row['count']} @ {row['offsets']}")

    print("\n=== CDCE full32 (external) hits ===")
    if not cdce["external_full32"]:
        print("  (none)")
    for row in cdce["external_full32"]:
        print(f"  reg{row['reg']:X} {row['full32']} {row['endian']} ×{row['count']} @ {row['offsets']}")

    print("\n=== CDCE SCAA090 REG0 ===")
    print("  (none)" if not cdce["scaa090"] else cdce["scaa090"])

    print("\n=== CDCE data28-only (weaker) ===")
    print(f"  rows: {len(cdce['data28_only'])} (see JSON for detail)")

    print("\n=== ADC 16-bit frames (noisy; focus 0x4180) ===")
    for row in adc:
        if row["name"] in ("ddr_lvds_0x41_80", "test_ramp_0x62", "soft_reset_0x00"):
            print(f"  {row['name']} {row['endian']} ×{row['count']} sample={row['offsets_sample']}")

    print("\n=== Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    if args.json_out:
        outp = Path(args.json_out)
        outp.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote {outp}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
