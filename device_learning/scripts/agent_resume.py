#!/usr/bin/env python3
"""Print concise resume instructions for human or agent after static phase closure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "manifests" / "handoff_bundle.json"


def main() -> int:
    if not BUNDLE.exists():
        print("Missing handoff_bundle.json — run: make bundle", file=sys.stderr)
        return 1

    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    closure = bundle.get("sections", {}).get("manifests_static_closure", {})
    readiness = bundle.get("sections", {}).get("manifests_phase_b_readiness", {})
    transition = bundle.get("sections", {}).get("manifests_phase_transition", {})

    print(json.dumps(
        {
            "task": "resume_phase_b",
            "declaration": bundle.get("declaration"),
            "static_closed": closure.get("static_phase_closed"),
            "identifiers": closure.get("identifiers"),
            "pytest_count": closure.get("pytest_count"),
            "recommended_phase": transition.get("recommended_phase"),
            "phase_b_checklist": readiness.get("checklist"),
            "required_artifacts": [
                "phase_b/captures/eeprom.bin",
                "phase_b/captures/usb_enum.pcapng",
                "phase_b/captures/usb_session.pcapng",
            ],
            "commands": bundle.get("resume_commands", []),
            "do_not": [
                "Do not treat synthetic fixture as device truth",
                "Do not auto-apply phase_b_upgrade_proposals to catalogs",
                "Do not add sensitive product model strings to manifests",
            ],
            "entrypoint": "make intake",
        },
        indent=2,
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
