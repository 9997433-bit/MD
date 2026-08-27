#!/usr/bin/env python3
"""Build static-phase closure summary (human + JSON)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "manifests" / "static_closure.json"
OUT_MD = ROOT / "STATIC_CLOSURE.md"


def pytest_count() -> int:
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=ROOT,
            text=True,
        )
        return len([ln for ln in out.splitlines() if "::" in ln])
    except subprocess.CalledProcessError:
        return 0


def load(rel: str) -> dict:
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main() -> None:
    cov = load("coverage.json")
    freeze = load("manifests/static_freeze.json")
    closed = load("manifests/static_phase_closed.json")
    readiness = load("manifests/phase_b_readiness.json")
    proposals = load("manifests/phase_b_upgrade_proposals.json")
    tests = pytest_count()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "declaration": cov.get("declaration"),
        "static_phase_closed": closed.get("static_phase_closed", False),
        "frozen": freeze.get("static_phase_complete", False),
        "identifiers": cov.get("total_identifiers"),
        "status_counts": cov.get("status_counts"),
        "pytest_count": tests,
        "manifest_json_count": len(list((ROOT / "manifests").glob("*.json"))),
        "phase_b_blockers_remaining": readiness.get("blocker_count", 0) - readiness.get("ready_count", 0),
        "upgrade_proposals_pending": proposals.get("proposal_count", 0),
        "resume_commands": [
            "make handoff",
            "make readiness",
            "make check-captures",
            "make phase-b",
            "make proposals",
            "make phase-c",
        ],
        "resume_artifacts": closed.get("resume_with", []),
        "boundary": "No further catalog status upgrades without hardware evidence",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = report.get("status_counts") or {}
    lines = [
        "# 静态阶段关闭摘要",
        "",
        f"**生成时间**：{report['generated_at']}",
        "",
        report["declaration"],
        "",
        "## 验收",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| 静态关闭 | `{report['static_phase_closed']}` |",
        f"| 冻结 | `{report['frozen']}` |",
        f"| Identifier | **{report['identifiers']}** |",
        f"| confirmed | {counts.get('confirmed', '?')} |",
        f"| blocked 类 | missing {counts.get('missing', '?')} + unknown {counts.get('unknown', '?')} + not_started {counts.get('not_started', '?')} |",
        f"| pytest | **{tests}** |",
        f"| manifest JSON | {report['manifest_json_count']} |",
        "",
        "## 静态阶段不再扩展",
        "",
        "在无实机证据前，不新增 identifier、不升级 catalog status。",
        "",
        "## 恢复工作所需采集物",
        "",
    ]
    for art in report["resume_artifacts"]:
        lines.append(f"- `{art}`")
    lines.extend(
        [
            "",
            "## 恢复命令",
            "",
            "```bash",
            "cd device_learning",
        ]
    )
    for cmd in report["resume_commands"]:
        lines.append(cmd)
    lines.extend(["```", "", "详见 `HARDWARE_HANDOFF.md` 与 `PHASE_B_READINESS.md`。"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"static_phase_closed": report["static_phase_closed"], "pytest_count": tests}, indent=2))


if __name__ == "__main__":
    main()
