#!/usr/bin/env python3
"""
核验「二进制基准」轨 B-Must（见 06_docs/二进制基准_分析计划与目标.md）。

不替代 audit_must.py（总目标 Must）；本脚本只回答：离线位流基线是否收束。

退出码：0=B-Must 全过；1=未过；2=缺文件
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCS = ROOT / "assets" / "firmware" / "20230825_s2056.mcs"
BIN = ROOT / "assets" / "firmware" / "20230825_s2056.bin"
PLAN = ROOT / "06_docs" / "二进制基准_分析计划与目标.md"

MCS_SHA = "dc91db8e4b80e0b6b971cf03e8b95e6eafc1905e390a80c1ba2625b5e67507c0"
BIN_SHA = "7587ee1c0316f0be2e30c4fb934d24276701ffbc142f51b3d9e907c7b47615d1"

REQUIRED_DOCS = [
    ROOT / "02_firmware" / "位流特征与软核线索.md",
    ROOT / "02_firmware" / "位流SPI常量搜索.md",
    ROOT / "02_firmware" / "位流网络常量搜索.md",
    ROOT / "02_firmware" / "位流BRAM帧分析.md",
    ROOT / "02_firmware" / "KC705_DDS_SPI_MIF对照.md",
    ROOT / "02_firmware" / "prjxray_K160T帧图可得性.md",
    ROOT / "02_firmware" / "位流逆向_能推出与不能.md",
    PLAN,
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bin() -> tuple[bytes, str]:
    if BIN.is_file():
        return BIN.read_bytes(), BIN.name
    sys.path.insert(0, str(ROOT / "scripts"))
    from parse_mcs import parse_mcs  # type: ignore

    return bytes(parse_mcs(MCS)), "mcs→bin"


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED_DOCS if not p.is_file()]
    if not MCS.is_file():
        print("缺少 mcs", file=sys.stderr)
        return 2
    if missing:
        print("缺文档:", *missing, sep="\n  ", file=sys.stderr)
        return 2

    mcs_ok = sha256_file(MCS) == MCS_SHA
    print(f"hash {MCS.name}: {'OK' if mcs_ok else 'FAIL'}")

    blob, src = load_bin()
    bin_ok = sha256_bytes(blob) == BIN_SHA
    print(f"hash bin({src}): {'OK' if bin_ok else 'FAIL'} len={len(blob)}")

    hash_ok = mcs_ok and bin_ok
    plan = PLAN.read_text(encoding="utf-8")
    has_gate = "假说 → 实测门禁映射" in plan
    has_b5 = "B5" in plan and "G2" in plan
    print(f"B-Must-1 identity hashes: {hash_ok}")
    print("B-Must-2/3 docs present: True")
    print(f"B-Must-4 gate map in plan: {has_gate and has_b5}")

    g0 = (ROOT / "06_docs" / "G0_命题基线证据表.md").read_text(encoding="utf-8")
    grades = {
        m.group(1): m.group(2).strip()
        for m in re.finditer(
            r"###\s+(P1\.\d)\s+[^\n—]*——\s*当前\s+\*\*([^*]+)\*\*", g0
        )
    }
    p13, p14 = grades.get("P1.3", ""), grades.get("P1.4", "")
    inbox = ROOT / "05_tests" / "g2_inbox" / "g2_clocks.json"
    spi = list((ROOT / "05_tests" / "g2_inbox").glob("spi*.csv"))
    if inbox.is_file() or spi:
        discipline = True
        print("note: measured inbox present → B-Must-5 N/A (handoff)")
    else:
        discipline = p13 == "❓" and p14 == "❓"
        print(f"B-Must-5 no fake P1.3/P1.4 ✅: {discipline} (P1.3={p13!r} P1.4={p14!r})")

    ok = hash_ok and has_gate and has_b5 and discipline
    print(f"B_MUST_ALL={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
