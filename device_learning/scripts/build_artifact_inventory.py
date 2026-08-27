#!/usr/bin/env python3
"""Inventory all generated artifacts in the learning package."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORE_ARTIFACTS = [
    ("EvidenceLedger.json", "主账本"),
    ("coverage.json", "完成度统计"),
    ("bridge_matrix.json", "强制 null 桥"),
    ("STATIC_REPORT.md", "静态摘要"),
    ("CONFIRMED_REPORT.md", "confirmed 项报告"),
    ("BLOCKED_REPORT.md", "阻塞项报告"),
    ("BRIDGE_REPORT.md", "null 桥报告"),
    ("ARCHITECTURE.md", "系统架构 mermaid 图"),
    ("IDENTIFIER_INDEX.md", "identifier 全表"),
    ("HARDWARE_HANDOFF.md", "实机接入指南"),
    ("phase_b/CHECKLIST.json", "阶段 B 机器可读检查清单"),
    ("manifests/static_freeze.json", "静态阶段冻结记录"),
    ("manifests/output_hashes.json", "产物哈希"),
]


def main() -> None:
    items = []
    seen: set[str] = set()
    for rel, desc in CORE_ARTIFACTS:
        path = ROOT / rel
        items.append({"path": rel, "description": desc, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
        seen.add(rel)

    for path in sorted((ROOT / "manifests").glob("*.json")):
        rel = f"manifests/{path.name}"
        if rel not in seen:
            items.append({"path": rel, "description": "generated manifest", "exists": True, "size_bytes": path.stat().st_size})
            seen.add(rel)

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(items),
        "present_count": sum(1 for i in items if i["exists"]),
        "artifacts": items,
    }
    out = ROOT / "manifests" / "artifact_inventory.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"present_count": meta["present_count"], "artifact_count": meta["artifact_count"]}, indent=2))


if __name__ == "__main__":
    main()
