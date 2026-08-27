#!/usr/bin/env python3
"""Run phase C experiment log validation and checklist sync."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(name: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / name)], cwd=ROOT, check=True)


def main() -> int:
    run("validate_experiment_log.py")
    run("build_experiment_index.py")
    run("sync_phase_c_checklist.py")
    run("build_phase_c_readiness.py")
    print("\nPhase C logs processed. See manifests/experiment_index.json and PHASE_C_READINESS.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
