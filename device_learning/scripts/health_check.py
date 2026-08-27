#!/usr/bin/env python3
"""Single-entry package health check; exits 0 when learning package is healthy."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"
GITKEEP = CAPTURES / ".gitkeep"


def check(name: str, ok: bool, detail: str = "") -> bool:
    mark = "OK" if ok else "FAIL"
    msg = f"[{mark}] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return ok


def captures_clean() -> tuple[bool, str]:
    if not CAPTURES.exists():
        return False, "captures dir missing"
    extras = [p.name for p in CAPTURES.iterdir() if p.is_file() and p.name != ".gitkeep"]
    if extras:
        return False, f"unexpected files: {', '.join(extras)}"
    return True, ".gitkeep only"


def main() -> int:
    ok = True
    ok &= check("coverage.json", (ROOT / "coverage.json").exists())
    ok &= check("EvidenceLedger.json", (ROOT / "EvidenceLedger.json").exists())

    if (ROOT / "manifests" / "completion_status.json").exists():
        comp = json.loads((ROOT / "manifests" / "completion_status.json").read_text(encoding="utf-8"))
        ok &= check("static_phase_complete", comp.get("static_phase_complete") is True)
    else:
        ok &= check("completion_status", False)

    if (ROOT / "manifests" / "static_freeze.json").exists():
        freeze = json.loads((ROOT / "manifests" / "static_freeze.json").read_text(encoding="utf-8"))
        ok &= check("frozen", freeze.get("static_phase_complete") is True)
    else:
        ok &= check("static_freeze", False)

    ok &= check("phase_b_readiness", (ROOT / "PHASE_B_READINESS.md").exists())
    ok &= check("phase_c_readiness", (ROOT / "PHASE_C_READINESS.md").exists())
    ok &= check("static_closure", (ROOT / "STATIC_CLOSURE.md").exists())
    clean, detail = captures_clean()
    ok &= check("captures_dir_clean", clean, detail)
    ok &= check("captures_gitkeep", GITKEEP.is_file())

    manifest_dir = ROOT / "manifests"
    bad = []
    for p in manifest_dir.glob("*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            bad.append(p.name)
    ok &= check("manifests_json_valid", not bad, ", ".join(bad) if bad else f"{len(list(manifest_dir.glob('*.json')))} files")

    eeprom_meta = ROOT / "manifests" / "eeprom_meta.json"
    if eeprom_meta.exists():
        meta = json.loads(eeprom_meta.read_text(encoding="utf-8"))
        ok &= check(
            "no_observed_eeprom_without_capture",
            not (meta.get("status") == "observed" and not (CAPTURES / "eeprom.bin").exists()),
        )

    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"], cwd=ROOT, check=True, capture_output=True)
        ok &= check("pytest", True)
    except subprocess.CalledProcessError as e:
        ok &= check("pytest", False, (e.stdout or b"").decode()[-200:])

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
