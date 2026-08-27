#!/usr/bin/env python3
"""Build unified package manifest (version, metrics, freeze, next steps)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pytest_count() -> int:
    try:
        out = subprocess.check_output(
            [__import__("sys").executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=ROOT,
            text=True,
        )
        return len([ln for ln in out.splitlines() if "::" in ln])
    except subprocess.CalledProcessError:
        return 0


def main() -> None:
    freeze = json.loads((ROOT / "manifests" / "static_freeze.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "manifests" / "evidence_summary.json").read_text(encoding="utf-8"))
    transition = json.loads((ROOT / "manifests" / "phase_transition.json").read_text(encoding="utf-8"))
    b_chk = json.loads((ROOT / "phase_b" / "CHECKLIST.json").read_text(encoding="utf-8"))

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": "device_learning",
        "version": "static-1.0",
        "phase": summary.get("phase"),
        "static_phase_complete": freeze.get("static_phase_complete"),
        "frozen_at": freeze.get("frozen_at"),
        "metrics": {
            "identifiers": summary.get("identifiers"),
            "confirmed": summary.get("status_counts", {}).get("confirmed"),
            "blocked": summary.get("blocked"),
            "pytest_count": pytest_count(),
            "manifest_json_count": len(list((ROOT / "manifests").glob("*.json"))),
        },
        "input_hashes": {
            "combined_output_sha256": freeze.get("output_combined_sha256"),
        },
        "checklists": {
            "phase_b": f"{b_chk.get('done_count', 0)}/{b_chk.get('total_count', 0)}",
            "phase_b_status": b_chk.get("status"),
        },
        "recommended_next_phase": transition.get("recommended_phase"),
        "next_actions": [
            "Place phase_b/captures/eeprom.bin (8192 bytes, real device dump)",
            "Place phase_b/captures/*.pcapng (USB captures)",
            "Run: make phase-b",
            "See: HARDWARE_HANDOFF.md",
        ],
        "declaration": summary.get("declaration"),
        "boundary": "Static phase frozen; no further status upgrades without hardware evidence",
    }
    out = ROOT / "manifests" / "package_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"version": manifest["version"], "pytest_count": manifest["metrics"]["pytest_count"]}, indent=2))


if __name__ == "__main__":
    main()
