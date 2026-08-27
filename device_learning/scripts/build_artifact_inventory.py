#!/usr/bin/env python3
"""Inventory all generated artifacts in the learning package."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = [
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
    ("manifests/evidence_summary.json", "一页式证据摘要"),
    ("manifests/pending_index.json", "阻塞项索引"),
    ("manifests/phase_roadmap.json", "阶段路线图"),
    ("manifests/catalog_integrity.json", "目录完整性校验"),
    ("manifests/sensitive_audit.json", "敏感词审计"),
    ("manifests/frame_summary.json", "位流帧摘要"),
    ("manifests/frame_deep.json", "位流深层扫描"),
    ("manifests/hardware_bom.json", "硬件 BOM"),
    ("manifests/eeprom_meta.json", "EEPROM 元数据"),
    ("manifests/photo_hw_map.json", "照片 HW 映射"),
]


def main() -> None:
    items = []
    for rel, desc in ARTIFACTS:
        path = ROOT / rel
        items.append(
            {
                "path": rel,
                "description": desc,
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(items),
        "present_count": sum(1 for i in items if i["exists"]),
        "artifacts": items,
    }
    out = ROOT / "manifests" / "artifact_inventory.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"present_count": meta["present_count"]}, indent=2))


if __name__ == "__main__":
    main()
