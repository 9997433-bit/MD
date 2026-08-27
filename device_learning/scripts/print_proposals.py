#!/usr/bin/env python3
"""Print human-readable phase B upgrade proposals for catalog review."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = ROOT / "manifests" / "phase_b_upgrade_proposals.json"
    if not path.exists():
        print("No proposals manifest. Run: make phase-b or make verify")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    print("=" * 60)
    print("阶段 B 升级建议（需人工审阅，不自动应用）")
    print("=" * 60)
    print(f"适用: {data.get('applicable')}")
    print(f"建议数: {data.get('proposal_count', 0)}")
    for note in data.get("notes", []):
        print(f"  · {note}")
    print()
    for p in data.get("proposals", []):
        print(f"{p['identifier']}")
        print(f"  {p['current_status']} → {p['proposed_status']}")
        print(f"  理由: {p['reason']}")
        print(f"  证据: {p['evidence']}")
        print()
    print("边界:", data.get("boundary"))
    print("=" * 60)


if __name__ == "__main__":
    main()
