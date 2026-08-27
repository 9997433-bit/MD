#!/usr/bin/env python3
"""Run phase B ingest pipeline and refresh the ledger."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "phase_b" / "captures"
SCRIPTS = ROOT / "scripts"


def has_captures() -> bool:
    if not CAPTURES.exists():
        return False
    names = {p.name for p in CAPTURES.iterdir() if p.is_file() and not p.name.startswith(".")}
    return bool(names & {"eeprom.bin"} or any(n.endswith((".pcap", ".pcapng")) for n in names))


def run(script: str, *args: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print(f"\n>>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> int:
    if not has_captures():
        print("No phase B captures found in phase_b/captures/")
        print("See HARDWARE_HANDOFF.md for placement instructions.")
        print("Running ledger refresh only (synthetic fixture path).")

    run("ingest_phase_b.py")
    run("analyze_pcap_stub.py")
    if (CAPTURES / "eeprom.bin").exists():
        run("analyze_eeprom.py")
        run("scan_firmware_stub.py")
    run("generate_ledger.py")
    run("verify_completion.py")

    status = json.loads((ROOT / "manifests" / "phase_b_status.json").read_text(encoding="utf-8"))
    if status.get("ready_for_ledger_refresh"):
        print("\nPhase B captures ingested. Review manifests/ and EvidenceLedger.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
