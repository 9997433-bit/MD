#!/usr/bin/env python3
"""Generate mermaid architecture diagram from system_map.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sysmap = json.loads((ROOT / "manifests" / "system_map.json").read_text(encoding="utf-8"))
    lines = [
        "# 系统架构图（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for edge in sysmap.get("edges", []):
        label = edge.get("type", "")
        status = edge.get("status", "")
        lines.append(f'  {edge["from"]} -->|"{label} ({status})"| {edge["to"]}')

    lines += [
        "```",
        "",
        "## 节点",
        "",
        "| Node | Layer | Status |",
        "|------|-------|--------|",
    ]
    for node in sysmap.get("nodes", []):
        lines.append(f"| `{node['id']}` | {node['layer']} | {node['status']} |")

    lines += [
        "",
        "证据来源：`manifests/system_map.json`",
        "",
    ]
    out = ROOT / "ARCHITECTURE.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
