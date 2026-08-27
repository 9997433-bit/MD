#!/usr/bin/env python3
"""Generate human-readable forced-null bridge policy report."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    bridges = json.loads((ROOT / "bridge_matrix.json").read_text(encoding="utf-8"))
    lines = [
        "# 强制 Null 桥报告（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**策略**：{bridges.get('policy', '')}",
        "",
        "> 无新证据前禁止将 null 桥升级为 proven_bridge",
        "",
        "| Bridge | Status | Reason |",
        "|--------|--------|--------|",
    ]
    for entry in bridges.get("entries", []):
        reason = (entry.get("reason") or "—").replace("|", "/")
        lines.append(f"| `{entry.get('bridge', '')}` | null | {reason} |")

    lines += [
        "",
        f"共 **{len(bridges.get('entries', []))}** 条强制 null 桥。",
        "",
    ]
    out = ROOT / "BRIDGE_REPORT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
