#!/usr/bin/env python3
"""Propose catalog status upgrades from observed phase B evidence (advisory only).

Does NOT modify catalog Python files automatically — human review required.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "manifests" / "phase_b_upgrade_proposals.json"


def load_json(rel: str) -> dict:
    path = ROOT / rel
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def current_status(identifier: str) -> str | None:
    catalogs = ["catalog_usb", "catalog_learn", "catalog_signal", "catalog_exp"]
    for name in catalogs:
        try:
            mod = __import__(f"catalogs.{name}", fromlist=["ENTRIES"])
            for e in getattr(mod, "ENTRIES", []):
                if e["identifier"] == identifier:
                    return e["status"]
        except Exception:
            continue
    return None


def propose(identifier: str, proposed: str, reason: str, evidence: str) -> dict | None:
    cur = current_status(identifier)
    if cur is None or cur == proposed:
        return None
    return {
        "identifier": identifier,
        "current_status": cur,
        "proposed_status": proposed,
        "reason": reason,
        "evidence": evidence,
        "requires_human_review": True,
    }


def build_proposals() -> dict:
    eeprom = load_json("manifests/eeprom_meta.json")
    usb = load_json("manifests/usb_capture_meta.json")
    fw_extract = load_json("manifests/firmware_extract.json")
    fw_scan = load_json("manifests/firmware_scan.json")
    proto_log = load_json("manifests/protocol_log_meta.json")
    eeprom_path = ROOT / "phase_b" / "captures" / "eeprom.bin"

    proposals: list[dict] = []
    applicable = False
    notes: list[str] = []

    if eeprom.get("status") == "observed" and eeprom_path.is_file():
        applicable = True
        notes.append("Real EEPROM dump detected (not synthetic fixture).")
        if p := propose("FW-EEPROM-IMAGE", "candidate", "8192-byte dump on disk", "phase_b/captures/eeprom.bin"):
            proposals.append(p)
        if eeprom.get("boot_format"):
            if p := propose(
                "FW-EEPROM-BOOT-FORMAT",
                "candidate",
                f"boot_format parsed as {eeprom['boot_format']}",
                "manifests/eeprom_meta.json",
            ):
                proposals.append(p)
            if p := propose(
                "FW-EEPROM-CONFIG-BYTE",
                "candidate",
                "boot_config_byte read from dump",
                "manifests/eeprom_meta.json",
            ):
                proposals.append(p)
        vid = eeprom.get("vid_hex")
        pid = eeprom.get("pid_hex")
        if vid and pid and vid not in ("0x0000", None) and pid not in ("0x0000", None):
            if p := propose("FW-EEPROM-VIDPID", "candidate", f"VID/PID fields read: {vid}/{pid}", "manifests/eeprom_meta.json"):
                proposals.append(p)
        if eeprom.get("did_hex"):
            if p := propose("FW-EEPROM-DID-FIELD", "candidate", "DID field read from dump", "manifests/eeprom_meta.json"):
                proposals.append(p)
        if eeprom.get("firmware_offset") is not None:
            if p := propose("FW-EEPROM-FW-RECORDS", "candidate", "C2 data-record region located", "manifests/eeprom_meta.json"):
                proposals.append(p)
        if fw_extract.get("status") == "extracted":
            if p := propose("FW-MCU-CORE-IMAGE", "candidate", "Firmware slice extracted for analysis", "phase_b/analysis/firmware.bin"):
                proposals.append(p)
        if fw_scan.get("firmware_scan", {}).get("status") == "observed":
            if p := propose("FW-MCU-RESET-VECTOR", "unknown", "Firmware bytes present; entry not disassembled", "manifests/firmware_scan.json"):
                proposals.append(p)

    elif eeprom.get("status") == "observed":
        notes.append(
            "Ignoring observed EEPROM metadata because phase_b/captures/eeprom.bin is absent; "
            "no FW-EEPROM-* proposals."
        )
    elif eeprom.get("status") == "synthetic_pipeline_test":
        notes.append("Only synthetic EEPROM available — no upgrade proposals.")

    decode = load_json("manifests/usb_protocol_decode.json")
    has_usb_files = (ROOT / "phase_b" / "captures" / "usb_enum.pcapng").exists() or (
        ROOT / "phase_b" / "captures" / "usb_session.pcapng"
    ).exists()

    # Only propose from decode when real pcap files are on disk (pytest empties captures/).
    if decode.get("status") == "decoded" and has_usb_files:
        applicable = True
        notes.append("usb_protocol_decode.json available — descriptor/endpoint map decoded.")
        evid = "manifests/usb_protocol_decode.json"
        for ident, reason in (
            ("PROTO-DESC-DEVICE", "Device descriptor decoded (VID/PID/bcdDevice)"),
            ("PROTO-DESC-CONFIG", "Configuration descriptor decoded (1 interface)"),
            ("PROTO-DESC-INTERFACE", "Interface descriptor decoded (vendor-specific 0xff, 4 EPs)"),
        ):
            if p := propose(ident, "confirmed", reason, evid):
                proposals.append(p)
        if p := propose(
            "PROTO-DESC-STRING",
            "candidate",
            "String descriptors partial (serial candidate present; manufacturer/product sparse)",
            evid,
        ):
            proposals.append(p)
        if p := propose("PROTO-EP-MAP", "confirmed", "Four bulk endpoints mapped (0x01/0x81/0x06/0x84)", evid):
            proposals.append(p)
        if p := propose("PROTO-EP-BULK-IN", "confirmed", "Bulk IN 0x81 and 0x84, wMaxPacketSize=512", evid):
            proposals.append(p)
        if p := propose("PROTO-EP-BULK-OUT", "confirmed", "Bulk OUT 0x01 and 0x06, wMaxPacketSize=512", evid):
            proposals.append(p)
        if p := propose(
            "PROTO-EP-INTERRUPT",
            "candidate",
            "No interrupt endpoint in interface descriptor (4 bulk only)",
            evid,
        ):
            proposals.append(p)
        if p := propose(
            "PROTO-EP-ALT-SETTINGS",
            "candidate",
            "Only bAlternateSetting=0 observed",
            evid,
        ):
            proposals.append(p)
        if p := propose("PROTO-XFER-MODE", "confirmed", "Session traffic is bulk-dominant; no isochronous", evid):
            proposals.append(p)
        if p := propose(
            "PROTO-CTRL-VENDOR-REQ",
            "candidate",
            "Primary: no vendor ctrl; companion FX2 0xA0/A4/A5/B0 tabulated",
            "manifests/usb_primary_ctrl_744f.json + manifests/usb_vendor_ctrl_7317.json",
        ):
            proposals.append(p)
        if p := propose(
            "LEARN-010-USB-PROTO",
            "candidate",
            "Framing 100% on EP01/81; opcode meanings still open",
            "manifests/usb_command_taxonomy.json",
        ):
            proposals.append(p)
        if p := propose(
            "EXP-011-PROTO-TABLE",
            "candidate",
            "14 observed opcode byte values cataloged; meanings remain unknown",
            "manifests/usb_command_taxonomy.json",
        ):
            proposals.append(p)
        if p := propose(
            "SIG-PROTOCOL-FRAMING",
            "candidate",
            "BE u16 tag + frame_len + body_len + type + opcode (100% length match)",
            "manifests/usb_command_taxonomy.json",
        ):
            proposals.append(p)
        if p := propose(
            "DRV-FIRMWARE-LOADER",
            "candidate",
            "FX2 RAM load via 0xA0/CPUCS then renumeration 0x7317→0x744f",
            "manifests/usb_vendor_ctrl_7317.json",
        ):
            proposals.append(p)
        if p := propose(
            "DRV-PIPE-EP-BIND",
            "candidate",
            "Cmd EP01/81 + data EP06/84 observed in session",
            "manifests/usb_command_taxonomy.json + manifests/usb_data_plane_hypothesis.json",
        ):
            proposals.append(p)
        if p := propose(
            "FW-MCU-RENUMERATION",
            "candidate",
            "Observed companion→primary renumeration after RAM load",
            "manifests/usb_enum_decode_notes.json + manifests/usb_vendor_ctrl_7317.json",
        ):
            proposals.append(p)
    elif usb.get("status") == "observed" and has_usb_files:
        applicable = True
        notes.append("USB capture files present; decode pending.")
        for ident in (
            "PROTO-DESC-DEVICE",
            "PROTO-DESC-CONFIG",
            "PROTO-DESC-INTERFACE",
            "PROTO-DESC-STRING",
        ):
            if p := propose(ident, "candidate", "pcap present; run analyze_usb_pcap_decode.py", "manifests/usb_capture_meta.json"):
                proposals.append(p)
        if p := propose("PROTO-EP-MAP", "candidate", "pcap present; endpoint map pending decode", "manifests/usb_capture_meta.json"):
            proposals.append(p)

    if proto_log.get("status") == "observed":
        applicable = True
        notes.append("protocol_log.json present (human/auto draft).")
        # Do not propose a downgrade; framing lives on bulk, not EP0 vendor ctrl.

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "applicable": applicable,
        "proposal_count": len(proposals),
        "proposals": proposals,
        "notes": notes,
        "boundary": "Advisory only; edit catalogs/*.py after human review — never auto-apply",
    }


def main() -> None:
    report = build_proposals()
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"proposal_count": report["proposal_count"], "applicable": report["applicable"]}, indent=2))


if __name__ == "__main__":
    main()
