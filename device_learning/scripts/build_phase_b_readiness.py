#!/usr/bin/env python3
"""Human-readable phase B readiness report (what is missing before deep analysis)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "manifests" / "phase_b_readiness.json"
OUT_MD = ROOT / "PHASE_B_READINESS.md"

BLOCKERS = [
    {
        "id": "eeprom",
        "label": "EEPROM 全片镜像",
        "artifact": "phase_b/captures/eeprom.bin",
        "unblocks": "FW-EEPROM-*, FW-MCU-* (partial)",
    },
    {
        "id": "usb_enum",
        "label": "USB 枚举抓包",
        "artifact": "phase_b/captures/usb_enum.pcapng",
        "unblocks": "PROTO-DESC-*",
    },
    {
        "id": "usb_session",
        "label": "USB 工作会话抓包",
        "artifact": "phase_b/captures/usb_session.pcapng",
        "unblocks": "PROTO-EP-*, SIG-* (partial)",
    },
]


def load_json(rel: str) -> dict:
    path = ROOT / rel
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    capture = load_json("manifests/capture_manifest.json")
    proposals = load_json("manifests/phase_b_upgrade_proposals.json")
    checklist = load_json("phase_b/CHECKLIST.json")

    items = []
    for b in BLOCKERS:
        path = ROOT / b["artifact"]
        row = {**b, "present": path.is_file(), "size_bytes": path.stat().st_size if path.is_file() else None}
        items.append(row)

    ready_count = sum(1 for i in items if i["present"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "blockers": items,
        "ready_count": ready_count,
        "blocker_count": len(items),
        "deep_analysis_ready": capture.get("ready_for_deep_analysis", False),
        "checklist": f"{checklist.get('done_count', 0)}/{checklist.get('total_count', 0)}",
        "upgrade_proposals_pending": proposals.get("proposal_count", 0),
        "next_command": "make check-captures" if ready_count == 0 else "make phase-b",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 阶段 B 就绪报告",
        "",
        f"**生成时间**：{report['generated_at']}",
        "",
        report["declaration"],
        "",
        f"- 检查清单进度：**{report['checklist']}**",
        f"- 深度分析就绪：`{report['deep_analysis_ready']}`",
        f"- 待审升级建议：**{report['upgrade_proposals_pending']}** 条",
        "",
        "## 阻塞项",
        "",
        "| 项 | 文件 | 状态 | 可解锁 |",
        "|----|------|------|--------|",
    ]
    for i in items:
        status = "✓ 已放置" if i["present"] else "· 缺失"
        lines.append(f"| {i['label']} | `{i['artifact']}` | {status} | {i['unblocks']} |")
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"```bash\ncd device_learning\n{report['next_command']}\n```",
            "",
            "详见 `HARDWARE_HANDOFF.md`。",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ready_count": ready_count, "deep_analysis_ready": report["deep_analysis_ready"]}, indent=2))


if __name__ == "__main__":
    main()
