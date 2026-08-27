#!/usr/bin/env python3
"""Generate human-readable report of confirmed identifiers."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_arch import ENTRIES as ARCH
from catalogs.catalog_bit import ENTRIES as BIT
from catalogs.catalog_exp import ENTRIES as EXP
from catalogs.catalog_hw import ENTRIES as HW
from catalogs.catalog_learn import ENTRIES as LEARN
from catalogs.catalog_ref import ENTRIES as REF
from catalogs.catalog_signal import ENTRIES as SIG
from catalogs.catalog_usb import ENTRIES as USB

CATALOGS = [("hw", HW), ("bit", BIT), ("signal", SIG), ("usb", USB), ("ref", REF), ("arch", ARCH), ("learn", LEARN), ("exp", EXP)]


def main() -> None:
    by_layer: dict[str, list] = defaultdict(list)
    total = 0
    for layer, entries in CATALOGS:
        for e in entries:
            if e["status"] == "confirmed":
                by_layer[layer].append(e)
                total += 1

    lines = [
        "# 已确认项报告（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**confirmed 总数**：{total} 条",
        "",
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "",
        "以下项有静态证据支撑；不含运行行为等价声明。",
        "",
    ]
    for layer in ("hw", "bit", "signal", "usb", "ref", "arch", "learn", "exp"):
        items = by_layer.get(layer, [])
        if not items:
            continue
        lines += [f"## {layer.upper()} ({len(items)})", ""]
        lines += ["| Identifier | Evidence |", "|------------|----------|"]
        for e in items:
            ev = (e.get("evidence") or "—").replace("|", "/")
            lines.append(f"| `{e['identifier']}` | {ev} |")
        lines.append("")

    out = ROOT / "CONFIRMED_REPORT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({total} confirmed)")


if __name__ == "__main__":
    main()
