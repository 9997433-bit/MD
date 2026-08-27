#!/usr/bin/env python3
"""Generate combined phase B/C checklist progress report."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render_checklist(data: dict) -> list[str]:
    lines = [f"### 阶段 {data.get('phase', '?')} — {data.get('status', '?')} ({data.get('done_count', 0)}/{data.get('total_count', 0)})", ""]
    lines += ["| ID | Task | Done |", "|----|------|------|"]
    for t in data.get("tasks", []):
        mark = "✓" if t.get("done") else "·"
        name = t.get("name") or t.get("experiment") or t.get("id")
        lines.append(f"| {t.get('id')} | {name} | {mark} |")
    lines.append("")
    return lines


def main() -> None:
    b = json.loads((ROOT / "phase_b" / "CHECKLIST.json").read_text(encoding="utf-8"))
    c = json.loads((ROOT / "phase_c" / "CHECKLIST.json").read_text(encoding="utf-8"))
    lines = [
        "# 阶段检查清单报告（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "",
    ]
    lines += render_checklist(b)
    lines += render_checklist(c)
    lines += ["## 下一步", "", "- 阶段 B：见 `HARDWARE_HANDOFF.md`", "- 阶段 C：见 `phase_c/README.md`", ""]
    out = ROOT / "CHECKLIST_REPORT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
