#!/usr/bin/env python3
"""Human-readable phase C readiness report."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "manifests" / "phase_c_readiness.json"
OUT_MD = ROOT / "PHASE_C_READINESS.md"


def load_json(rel: str) -> dict:
    path = ROOT / rel
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    checklist = load_json("phase_c/CHECKLIST.json")
    transition = load_json("manifests/phase_transition.json")
    experiments = load_json("manifests/experiment_index.json")

    phase_b_ready = transition.get("recommended_phase") in (
        "phase_b_in_progress",
        "phase_b_partial_complete",
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "phase_b_prerequisite_met": phase_b_ready,
        "checklist": f"{checklist.get('done_count', 0)}/{checklist.get('total_count', 0)}",
        "experiment_logs": experiments.get("entry_count", 0),
        "recommended_action": "make phase-c" if phase_b_ready else "complete phase B captures first",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 阶段 C 就绪报告",
        "",
        f"**生成时间**：{report['generated_at']}",
        "",
        report["declaration"],
        "",
        f"- 阶段 B 前置：`{report['phase_b_prerequisite_met']}`",
        f"- 检查清单：**{report['checklist']}**",
        f"- 实验日志数：**{report['experiment_logs']}**",
        "",
        "## 下一步",
        "",
        f"```bash\ncd device_learning\n{report['recommended_action']}\n```",
        "",
        "模板：`phase_c/templates/experiment_log_template.json`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
