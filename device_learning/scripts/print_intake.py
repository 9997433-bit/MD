#!/usr/bin/env python3
"""Print step-by-step intake guide when resuming after static phase closure."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str) -> dict:
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def file_status(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        return "缺失"
    if rel.endswith("eeprom.bin") and p.stat().st_size != 8192:
        return f"存在但大小异常 ({p.stat().st_size} B)"
    return f"已放置 ({p.stat().st_size} B)"


def main() -> None:
    closure = load("manifests/static_closure.json")
    readiness = load("manifests/phase_b_readiness.json")
    transition = load("manifests/phase_transition.json")

    print("=" * 60)
    print("device_learning — 实机接入向导")
    print("=" * 60)
    print(closure.get("declaration", ""))
    print()
    print(f"当前推荐阶段: {transition.get('recommended_phase', 'n/a')}")
    print(f"阶段 B 检查清单: {readiness.get('checklist', '?')}")
    print()

    artifacts = [
        "phase_b/captures/eeprom.bin",
        "phase_b/captures/usb_enum.pcapng",
        "phase_b/captures/usb_session.pcapng",
        "phase_b/captures/protocol_log.json",
    ]
    print("── 采集物状态 ──")
    for rel in artifacts:
        print(f"  [{file_status(rel)}] {rel}")
    print()

    steps = [
        ("1", "确认合法分析授权", "阅读 phase_b/templates/eeprom_read.md 前置检查"),
        ("2", "读取 EEPROM → eeprom.bin (8192 B)", "两次读取后: python3 scripts/diff_eeprom.py a.bin b.bin"),
        ("3", "USB 抓包 → usb_enum.pcapng / usb_session.pcapng", "模板: phase_b/templates/usb_capture.md"),
        ("4", "预检", "make check-captures"),
        ("5", "刷新账本", "make phase-b"),
        ("6", "审阅升级建议", "make proposals → 手动编辑 catalogs/*.py"),
        ("7", "固件切片", "python3 scripts/extract_firmware_slice.py"),
        ("8", "Ghidra 反汇编", "→ phase_b/analysis/mcu_disasm.txt"),
        ("9", "阶段 C 实验", "phase_c/logs/ + make phase-c"),
    ]
    print("── 推荐步骤 ──")
    for num, title, detail in steps:
        print(f"  {num}. {title}")
        print(f"      {detail}")
    print()
    print("── 诚实边界 ──")
    print("  · 合成夹具 (phase_b/fixtures/) 不代表设备真相")
    print("  · proposals 仅为建议，不自动改 catalog")
    print("  · 目录完整 ≠ 厂商等价 ≠ 掌握运行行为")
    print("=" * 60)


if __name__ == "__main__":
    main()
