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
STATUS_PATH = ROOT / "manifests" / "phase_b_status.json"


def has_captures() -> bool:
    if not CAPTURES.exists():
        return False
    names = {p.name for p in CAPTURES.iterdir() if p.is_file() and not p.name.startswith(".")}
    return bool(names & {"eeprom.bin"} or any(n.endswith((".pcap", ".pcapng")) for n in names))


def run(script: str, *args: str, check: bool = True) -> int:
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print(f"\n>>> {' '.join(cmd)}")
    completed = subprocess.run(cmd, check=False)
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, cmd)
    return completed.returncode


def load_status() -> dict:
    if STATUS_PATH.exists():
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    return {}


def main() -> int:
    if not has_captures():
        print("No phase B captures found in phase_b/captures/")
        print("See HARDWARE_HANDOFF.md for placement instructions.")
        print("Running ledger refresh only (no capture ingest).")

    run("ingest_phase_b.py")
    status = load_status()
    run("analyze_pcap_stub.py")
    run("analyze_usb_pcap_decode.py")
    run("analyze_usb_command_taxonomy.py")
    run("analyze_cmd_data_correlation.py")
    run("analyze_ep84_packing_deep.py")
    run("analyze_ep01_body_semantics.py")
    run("analyze_protocol_log.py")
    if (ROOT / "phase_b" / "analysis" / "fx2_ram_from_enum.bin").exists():
        run("analyze_fx2_ram_image.py")
        run("analyze_fx2_ram_xrefs.py")
        run("analyze_fx2_ram_routines.py")
        run("analyze_cmd_data_correlation.py")
        run("analyze_fx2_cmd_dispatch.py")
        run("analyze_fx2_datapath.py")
        run("analyze_fx2_ram_disasm.py")
        run("analyze_fx2_ivt_and_1435.py")
        run("analyze_fx2_stream_path.py")
        run("analyze_fx2_address_map.py")
        run("analyze_fx2_oracle_crosscheck.py")
    if (CAPTURES / "usb_session.pcapng").exists():
        run("unpack_ep84_candidate.py")
    run("analyze_restore_crosscheck.py")
    if (CAPTURES / "eeprom.bin").exists():
        run("analyze_eeprom.py")
        run("scan_firmware_stub.py")
        # Synthetic fixture returns 2; missing slice returns 3 — do not abort pipeline.
        run("extract_firmware_slice.py", check=False)
    run("build_capture_manifest.py")
    run("propose_phase_b_upgrades.py")
    run("build_phase_b_readiness.py")
    run("sync_phase_b_checklist.py")
    run("detect_phase_transition.py")
    run("generate_ledger.py")
    run("verify_completion.py")

    status = load_status()
    if status.get("ready_for_ledger_refresh"):
        print("\nPhase B captures ingested. Review manifests/ and EvidenceLedger.json.")
    else:
        print("\nLedger refreshed (static). Place captures and re-run make phase-b.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
