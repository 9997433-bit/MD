#!/usr/bin/env python3
"""Generate human-readable markdown index of all catalog identifiers."""
from __future__ import annotations

import json
import sys
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

CATALOGS = [
    ("hw", HW),
    ("bit", BIT),
    ("signal", SIG),
    ("usb", USB),
    ("ref", REF),
    ("arch", ARCH),
    ("learn", LEARN),
    ("exp", EXP),
]


def main() -> None:
    lines = [
        "# Identifier 索引（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "",
    ]
    total = 0
    for layer, entries in CATALOGS:
        lines += [f"## {layer.upper()} ({len(entries)})", ""]
        lines += ["| ID | Status | Description |", "|----|--------|-------------|"]
        for e in entries:
            desc = (e.get("description") or "")[:80].replace("|", "/")
            lines.append(f"| `{e['identifier']}` | {e['status']} | {desc} |")
        lines.append("")
        total += len(entries)

    lines += [f"**合计**：{total} 条", ""]
    out = ROOT / "IDENTIFIER_INDEX.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({total} identifiers)")


if __name__ == "__main__":
    main()
