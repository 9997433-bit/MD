#!/usr/bin/env python3
"""Verify static analysis completion criteria."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cov = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    checks = {
        "ledger_exists": (ROOT / "EvidenceLedger.json").exists(),
        "coverage_pass": cov.get("all_pass", False),
        "min_identifiers": cov.get("total_identifiers", 0) >= 200,
        "learning_guide": (ROOT / "LEARNING_GUIDE.md").exists(),
        "static_report": (ROOT / "STATIC_REPORT.md").exists(),
        "blocked_report": (ROOT / "BLOCKED_REPORT.md").exists(),
        "phase_b_scaffold": (ROOT / "phase_b" / "README.md").exists(),
        "phase_c_scaffold": (ROOT / "phase_c" / "README.md").exists(),
        "hardware_handoff": (ROOT / "HARDWARE_HANDOFF.md").exists(),
        "pending_index": (ROOT / "manifests" / "pending_index.json").exists(),
        "identifier_index": (ROOT / "IDENTIFIER_INDEX.md").exists(),
        "bom_crosswalk": (ROOT / "manifests" / "bom_crosswalk.json").exists(),
        "phase_roadmap": (ROOT / "manifests" / "phase_roadmap.json").exists(),
        "catalog_integrity": (ROOT / "manifests" / "catalog_integrity.json").exists(),
        "sensitive_audit_clean": json.loads(
            (ROOT / "manifests" / "sensitive_audit.json").read_text(encoding="utf-8")
        ).get("ok", False),
        "no_captures_yet": not (ROOT / "phase_b" / "captures" / "eeprom.bin").exists(),
    }
    result = {
        "static_phase_complete": all(checks[k] for k in checks if k != "no_captures_yet"),
        "checks": checks,
        "note": "static_phase_complete means L0-A deep done; phase B/C require hardware",
    }
    out = ROOT / "manifests" / "completion_status.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["static_phase_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
