#!/usr/bin/env python3
"""Generate human-readable static analysis report."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _idcode(frame: dict) -> str:
    reg = frame.get("packet_stream", {}).get("registers", {}).get("IDCODE", {})
    return reg.get("raw") or frame.get("idcode", {}).get("raw") or "N/A"


def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    cov = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    frame = json.loads((ROOT / "manifests" / "frame_summary.json").read_text(encoding="utf-8"))
    sysmap = json.loads((ROOT / "manifests" / "system_map.json").read_text(encoding="utf-8"))
    bom = json.loads((ROOT / "manifests" / "hardware_bom.json").read_text(encoding="utf-8"))
    pending = _load_json(ROOT / "manifests" / "pending_index.json")
    phase_b = _load_json(ROOT / "manifests" / "phase_b_status.json")
    bit_strings = _load_json(ROOT / "manifests" / "bit_strings.json")
    entropy = _load_json(ROOT / "manifests" / "config_entropy.json")
    crosswalk = _load_json(ROOT / "manifests" / "bom_crosswalk.json")
    board = bom.get("board_info", {})

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
        f"- 板卡版本：{board.get('board_revision', 'N/A')}",
        f"- BOM 组件：{len(bom.get('components', []))} 条",
        f"- 照片索引：10 张",
        "",
        "## 位流",
        "",
        f"- IDCODE：`{_idcode(frame)}`",
        f"- 帧长 FLR：{fa.get('frame_length_words', 'N/A')} words",
        f"- FDRI 字数：{fa.get('fdri_word_count', 'N/A')}",
        f"- 帧估计：{fa.get('estimated_frame_count', 'N/A')}",
        f"- IOB candidate 配置字：{fa.get('candidate_iob_config_words', 'N/A')}",
        f"- 位流字符串（脱敏）：{bit_strings.get('unique_redacted_count', 'N/A')} 条",
        f"- 配置段熵：{entropy.get('byte_entropy_bits', 'N/A')} bits/byte（零字节比 {entropy.get('zero_byte_ratio', 'N/A')}）",
        "",
        "## BOM 交叉对照",
        "",
        f"- 已链接组件：**{crosswalk.get('linked_count', 'N/A')}** / {crosswalk.get('component_count', 40)}",
        "",
        "## 待解项",
        "",
        f"- 阻塞 identifier：**{pending.get('total_blocked', 'N/A')}** 条（见 `manifests/pending_index.json`）",
        "",
        "## 数据路径",
        "",
    ]
    for edge in sysmap.get("edges", []):
        lines.append(f"- `{edge['from']}` → `{edge['to']}` ({edge['status']})")

    lines += [
        "",
        "## 阶段 B 状态",
        "",
        f"- EEPROM 已采集：{'是' if phase_b.get('flags', {}).get('eeprom_present') else '否'}",
        f"- USB 抓包已采集：{'是' if phase_b.get('flags', {}).get('usb_capture_present') else '否'}",
        "",
        "## 阻塞项（需实机）",
        "",
        "- EEPROM 转储 → `phase_b/captures/eeprom.bin`",
        "- USB 抓包 → `phase_b/captures/*.pcapng`",
        "- 实验验证 → 见 `phase_c/README.md`",
        "- 接入指南 → `HARDWARE_HANDOFF.md`",
        "- 阶段路线图 → `manifests/phase_roadmap.json`",
        "- 架构图 → `ARCHITECTURE.md`",
        "- Null 桥 → `BRIDGE_REPORT.md`",
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
