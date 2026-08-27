#!/usr/bin/env python3
"""Build a single JSON handoff bundle for phase B resume (no secrets)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manifests" / "handoff_bundle.json"

INCLUDE = [
    "manifests/static_closure.json",
    "manifests/static_phase_closed.json",
    "manifests/phase_b_readiness.json",
    "manifests/phase_c_readiness.json",
    "manifests/phase_transition.json",
    "manifests/capture_manifest.json",
    "manifests/phase_b_upgrade_proposals.json",
    "manifests/phase_roadmap.json",
    "manifests/evidence_summary.json",
    "phase_b/CHECKLIST.json",
    "phase_c/CHECKLIST.json",
]


def load(rel: str) -> dict | list | None:
    path = ROOT / rel
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"error": "invalid_json", "path": rel}


def main() -> None:
    bundle = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": "device_learning",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
        "resume_commands": [
            "make intake",
            "make check-captures",
            "make phase-b",
            "make proposals",
        ],
        "sections": {rel.replace("/", "_").replace(".json", ""): load(rel) for rel in INCLUDE},
        "boundary": "Bundle for human/agent handoff; not a device truth claim",
    }
    OUT.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pr_snapshot = ROOT / "manifests" / "pr_body_snapshot.md"
    pr_snapshot.write_text(
        subprocess.check_output([sys.executable, str(ROOT / "scripts" / "print_pr_body.py")], cwd=ROOT, text=True),
        encoding="utf-8",
    )
    print(json.dumps(
        {
            "path": str(OUT.relative_to(ROOT)),
            "sections": len(bundle["sections"]),
            "pr_body_snapshot": str(pr_snapshot.relative_to(ROOT)),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
