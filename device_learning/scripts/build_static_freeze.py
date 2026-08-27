#!/usr/bin/env python3
"""Write static-phase freeze record when all checks pass."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    completion = json.loads((ROOT / "manifests" / "completion_status.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "manifests" / "evidence_summary.json").read_text(encoding="utf-8"))
    outputs = json.loads((ROOT / "manifests" / "output_hashes.json").read_text(encoding="utf-8"))
    inputs = json.loads((ROOT / "manifests" / "file_hashes.json").read_text(encoding="utf-8"))

    freeze = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "phase": summary.get("phase"),
        "static_phase_complete": completion.get("static_phase_complete"),
        "identifiers": summary.get("identifiers"),
        "confirmed": summary.get("status_counts", {}).get("confirmed"),
        "blocked": summary.get("blocked"),
        "git_commit": git_head(),
        "input_file_count": inputs.get("file_count"),
        "output_combined_sha256": outputs.get("combined_sha256"),
        "declaration": summary.get("declaration"),
        "next_phase": "phase_b_hardware_capture",
        "stop_conditions_pass": summary.get("stop_conditions_pass"),
    }
    out = ROOT / "manifests" / "static_freeze.json"
    out.write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"static_phase_complete": freeze["static_phase_complete"]}, indent=2))


if __name__ == "__main__":
    main()
