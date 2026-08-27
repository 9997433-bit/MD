#!/usr/bin/env python3
"""Print human-readable handoff summary for phase B hardware capture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pkg = json.loads((ROOT / "manifests" / "package_manifest.json").read_text(encoding="utf-8"))
    print("=" * 60)
    print("device_learning — 实机交接摘要")
    print("=" * 60)
    print(f"包版本      : {pkg.get('version')}")
    print(f"阶段        : {pkg.get('phase')}")
    print(f"静态冻结    : {pkg.get('static_phase_complete')}")
    print(f"Identifier  : {pkg['metrics'].get('identifiers')} (confirmed {pkg['metrics'].get('confirmed')}, blocked {pkg['metrics'].get('blocked')})")
    print(f"pytest      : {pkg['metrics'].get('pytest_count')}")
    print(f"阶段 B 进度 : {pkg['checklists'].get('phase_b')} ({pkg['checklists'].get('phase_b_status')})")
    print()
    print("声明:", pkg.get("declaration"))
    print()
    print("── 你需要放入的文件 ──")
    print("  phase_b/captures/eeprom.bin      (8192 字节, 24LC64 全片)")
    print("  phase_b/captures/usb_enum.pcapng")
    print("  phase_b/captures/usb_session.pcapng")
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
