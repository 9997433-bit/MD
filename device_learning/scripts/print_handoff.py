#!/usr/bin/env python3
"""Print human-readable handoff summary for phase B hardware capture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str) -> dict:
    path = ROOT / rel
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    pkg = load_json("manifests/package_manifest.json")
    checklist = load_json("phase_b/CHECKLIST.json")
    roadmap = load_json("manifests/phase_roadmap.json")
    pending = load_json("manifests/pending_index.json")

    print("=" * 60)
    print("device_learning — 实机交接摘要")
    print("=" * 60)
    print(f"包版本      : {pkg.get('version')}")
    print(f"阶段        : {pkg.get('phase')}")
    print(f"静态冻结    : {pkg.get('static_phase_complete')}")
    metrics = pkg.get("metrics", {})
    print(
        f"Identifier  : {metrics.get('identifiers')} "
        f"(confirmed {metrics.get('confirmed')}, blocked {metrics.get('blocked')})"
    )
    print(f"pytest      : {metrics.get('pytest_count')}")
    cl = pkg.get("checklists", {})
    print(f"阶段 B 进度 : {cl.get('phase_b')} ({cl.get('phase_b_status')})")
    print()
    print("声明:", pkg.get("declaration"))
    print()

    done = checklist.get("done_count", 0)
    total = checklist.get("total_count", 0)
    print(f"── 阶段 B 检查清单 ({done}/{total}) ──")
    for task in checklist.get("tasks", []):
        mark = "✓" if task.get("done") else "·"
        opt = " (可选)" if task.get("optional") else ""
        art = task.get("artifact") or task.get("command", "")
        print(f"  {mark} {task.get('id')} {task.get('name')}{opt}")
        if art and not task.get("done"):
            print(f"      → {art}")
    print()

    eeprom_unblocks = len(roadmap.get("phase_b", [{}])[0].get("unblocks", [])) if roadmap.get("phase_b") else 0
    print("── 采集可解锁（路线图估计）──")
    print(f"  EEPROM 采集 → 约 {eeprom_unblocks} 条 FW-* blocked 项")
    print(f"  USB 抓包    → PROTO-* / SIG-* 层")
    print(f"  当前阻塞总数: {pending.get('total_blocked', '?')}")
    print()

    print("── 你需要放入的文件 ──")
    print("  phase_b/captures/eeprom.bin      (8192 字节, 24LC64 全片)")
    print("  phase_b/captures/usb_enum.pcapng")
    print("  phase_b/captures/usb_session.pcapng")
    print()
    print("── 采集前预检 ──")
    print("  python3 scripts/validate_captures.py")
    print()
    print("── 采集后执行 ──")
    print("  cd device_learning && make phase-b")
    print()
    print("── 详细文档 ──")
    print("  HARDWARE_HANDOFF.md")
    print("  phase_b/templates/eeprom_read.md")
    print("  phase_b/templates/usb_capture.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
