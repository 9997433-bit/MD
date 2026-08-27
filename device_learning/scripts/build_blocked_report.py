#!/usr/bin/env python3
"""Generate human-readable blocked-identifier report from pending_index.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pending = json.loads((ROOT / "manifests" / "pending_index.json").read_text(encoding="utf-8"))
    lines = [
        "# 阻塞项报告（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**阻塞总数**：{pending.get('total_blocked', 0)} 条",
        "",
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "",
    ]
    for status, block in pending.get("by_status", {}).items():
        items = block.get("items", [])
        lines += [f"## {status} ({len(items)})", ""]
        lines += ["| Identifier | Layer | Boundary |", "|------------|-------|----------|"]
        for item in items:
            b = (item.get("boundary") or "—").replace("|", "/")
            lines.append(f"| `{item['identifier']}` | {item['layer']} | {b} |")
        lines.append("")

    lines += [
        "## 解锁路线",
        "",
        "见 `manifests/phase_roadmap.json` 与 `HARDWARE_HANDOFF.md`。",
        "",
    ]
    out = ROOT / "BLOCKED_REPORT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
