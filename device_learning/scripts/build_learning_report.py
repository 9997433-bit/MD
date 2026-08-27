#!/usr/bin/env python3
"""Generate human-readable static analysis report."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cov = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    frame = json.loads((ROOT / "manifests" / "frame_summary.json").read_text(encoding="utf-8"))
    sysmap = json.loads((ROOT / "manifests" / "system_map.json").read_text(encoding="utf-8"))
    bom = json.loads((ROOT / "manifests" / "hardware_bom.json").read_text(encoding="utf-8"))

    fa = frame.get("frame_analysis", {})
    lines = [
        "# 静态分析报告（自动生成）",
        "",
        f"**生成时间**：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "",
        "## 摘要",
        "",
        f"- Identifier 总数：**{cov['total_identifiers']}**",
        f"- 停止条件：**{'全部通过' if cov['all_pass'] else '未通过'}**",
        f"- 阶段：**{cov.get('phase', 'unknown')}**",
        "",
        "### Status 分布",
        "",
        "| Status | 数量 |",
        "|--------|------|",
    ]
    for k, v in sorted(cov.get("status_counts", {}).items()):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## 硬件",
        "",
        f"- BOM 组件：{len(bom.get('components', []))} 条",
        f"- 照片索引：10 张",
        "",
        "## 位流",
        "",
        f"- IDCODE：`{fa.get('idcode', {}).get('raw', frame.get('packet_stream', {}).get('registers', {}).get('IDCODE', {}).get('raw', 'N/A'))}`",
        f"- 帧长 FLR：{fa.get('frame_length_words', 'N/A')} words",
        f"- FDRI 字数：{fa.get('fdri_word_count', 'N/A')}",
        f"- 帧估计：{fa.get('estimated_frame_count', 'N/A')}",
        f"- IOB candidate 配置字：{fa.get('candidate_iob_config_words', 'N/A')}",
        "",
        "## 数据路径",
        "",
    ]
    for edge in sysmap.get("edges", []):
        lines.append(f"- `{edge['from']}` → `{edge['to']}` ({edge['status']})")

    lines += [
        "",
        "## 阻塞项（需实机）",
        "",
        "- EEPROM 转储 → `phase_b/captures/eeprom.bin`",
        "- USB 抓包 → `phase_b/captures/*.pcapng`",
        "- 实验验证 → 见 `phase_c/README.md`",
        "",
        "## 重新生成",
        "",
        "```bash",
        "python3 scripts/generate_ledger.py",
        "python3 scripts/build_learning_report.py",
        "```",
        "",
    ]
    out = ROOT / "STATIC_REPORT.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
