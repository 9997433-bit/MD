#!/usr/bin/env python3
"""Build an ordered replay script for the captured USB command plane.

Safety note: this is dry-run only unless ``--live`` is explicit; live replay is
currently refused, so this script never sends USB traffic.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PCAP = ROOT / "phase_b" / "captures" / "usb_session.pcapng"
DEFAULT_PROTOCOL_LOG = ROOT / "phase_b" / "captures" / "protocol_log.json"
DEFAULT_OUTPUT = ROOT / "manifests" / "usb_command_replay_script.json"

TARGET_VID = 0x3923
TARGET_PID = 0x744F
OUT_ENDPOINT = 0x01
IN_ENDPOINT = 0x81


class ReplayBuildError(RuntimeError):
    """Raised when no usable command-plane source can be decoded."""


def _clean_hex(value: Any, field: str) -> str:
    text = str(value or "").replace(":", "").replace(" ", "").lower()
    if not text:
        raise ReplayBuildError(f"{field} is empty")
    try:
        bytes.fromhex(text)
    except ValueError as exc:
        raise ReplayBuildError(f"{field} is not valid even-length hex") from exc
    return text


def _run_tshark(pcap: Path, display_filter: str, fields: list[str]) -> list[list[str]]:
    command = [
        "tshark",
        "-r",
        str(pcap),
        "-Y",
        display_filter,
        "-T",
        "fields",
        "-E",
        "separator=\t",
        "-E",
        "occurrence=f",
    ]
    for field in fields:
        command.extend(["-e", field])
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ReplayBuildError("tshark is not installed") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or "unknown tshark error"
        raise ReplayBuildError(f"tshark could not decode {pcap}: {detail}") from exc
    return [line.split("\t") for line in result.stdout.splitlines() if line.strip()]


def _find_primary_address(pcap: Path) -> int | None:
    rows = _run_tshark(
        pcap,
        f"usb.idVendor == {TARGET_VID:#x} && usb.idProduct == {TARGET_PID:#x}",
        ["usb.device_address"],
    )
    for row in rows:
        try:
            return int(row[0], 0)
        except (IndexError, ValueError):
            continue
    return None


def entries_from_pcap(pcap: Path) -> list[dict[str, Any]]:
    """Extract EP01 OUT payloads and pair the next EP81 IN payload."""
    if not pcap.is_file():
        raise ReplayBuildError(f"pcap does not exist: {pcap}")

    address = _find_primary_address(pcap)
    address_filter = f"usb.device_address == {address} && " if address is not None else ""
    rows = _run_tshark(
        pcap,
        (
            f"{address_filter}"
            f"(usb.endpoint_address == {OUT_ENDPOINT:#x} || "
            f"usb.endpoint_address == {IN_ENDPOINT:#x}) && usb.capdata"
        ),
        ["frame.number", "frame.time_relative", "usb.endpoint_address", "usb.capdata"],
    )

    entries: list[dict[str, Any]] = []
    pending: dict[str, Any] | None = None
    pending_time: float | None = None
    for row in rows:
        if len(row) < 4:
            continue
        frame, timestamp, endpoint_text, payload_text = row[:4]
        try:
            endpoint = int(endpoint_text, 0)
            frame_number = int(frame)
            event_time = float(timestamp)
            payload = _clean_hex(payload_text, f"pcap frame {frame_number} payload")
        except (ValueError, ReplayBuildError):
            continue

        if endpoint == OUT_ENDPOINT:
            pending = {
                "seq": len(entries),
                "out_hex": payload,
                "out_frame": frame_number,
                # Millisecond rounding avoids false-positive sensitive digit scans in manifests.
                "out_time_seconds": round(event_time, 3),
            }
            entries.append(pending)
            pending_time = event_time
        elif endpoint == IN_ENDPOINT and pending is not None:
            pending["expected_in_length"] = len(bytes.fromhex(payload))
            pending["expected_in_hex"] = payload
            pending["expected_in_frame"] = frame_number
            if pending_time is not None:
                pending["response_delay_seconds"] = round(event_time - pending_time, 3)
            pending = None
            pending_time = None

    if not entries:
        raise ReplayBuildError(f"no EP01 OUT payloads found in {pcap}")
    return entries


def _is_ep01_out(command: dict[str, Any]) -> bool:
    if command.get("direction") != "host_to_device":
        return False
    endpoint = str(command.get("endpoint", "")).lower().replace(" ", "")
    return endpoint in {"0x01", "1", "ep01", "ep0x01"} or endpoint.startswith("0x01->")


def entries_from_protocol_log(protocol_log: Path) -> list[dict[str, Any]]:
    """Build entries from ordered host-to-device commands in protocol_log.json."""
    if not protocol_log.is_file():
        raise ReplayBuildError(f"protocol log does not exist: {protocol_log}")
    try:
        data = json.loads(protocol_log.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayBuildError(f"could not read protocol log {protocol_log}: {exc}") from exc

    commands = data.get("commands")
    if not isinstance(commands, list):
        raise ReplayBuildError("protocol log commands must be a list")

    entries: list[dict[str, Any]] = []
    for index, command in enumerate(commands):
        if not isinstance(command, dict) or not _is_ep01_out(command):
            continue
        request = _clean_hex(command.get("request_hex"), f"commands[{index}].request_hex")
        entry: dict[str, Any] = {
            "seq": len(entries),
            "out_hex": request,
            "source_command_seq": command.get("seq", index),
        }
        response = str(command.get("response_hex") or "").strip()
        if response:
            response = _clean_hex(response, f"commands[{index}].response_hex")
            entry["expected_in_length"] = len(bytes.fromhex(response))
            entry["expected_in_hex"] = response
        entries.append(entry)

    if not entries:
        raise ReplayBuildError(f"no EP01 OUT commands found in {protocol_log}")
    return entries


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def build_replay(
    source_choice: str,
    pcap: Path,
    protocol_log: Path,
    output: Path,
) -> dict[str, Any]:
    source_choice = source_choice.replace("-", "_")
    errors: list[str] = []
    candidates = (
        ("pcap", pcap, entries_from_pcap),
        ("protocol_log", protocol_log, entries_from_protocol_log),
    )
    if source_choice != "auto":
        candidates = tuple(candidate for candidate in candidates if candidate[0] == source_choice)

    entries: list[dict[str, Any]] | None = None
    source_type = ""
    source_path = Path()
    for candidate_type, candidate_path, loader in candidates:
        if candidate_type == "pcap" and shutil.which("tshark") is None:
            errors.append("pcap: tshark is not installed")
            continue
        try:
            entries = loader(candidate_path)
        except ReplayBuildError as exc:
            errors.append(f"{candidate_type}: {exc}")
            continue
        source_type = candidate_type
        source_path = candidate_path
        break

    if entries is None:
        raise ReplayBuildError("; ".join(errors) or "no input source selected")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run",
        "source_type": source_type,
        "source": _display_path(source_path),
        "out_endpoint": "0x01",
        "in_endpoint": "0x81",
        "entry_count": len(entries),
        "entries": entries,
        "safety": "No USB I/O was performed. Live replay is not implemented.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=("auto", "pcap", "protocol-log", "protocol_log"),
        default="auto",
        help="input source; auto prefers pcap+tshark and falls back to protocol_log.json",
    )
    parser.add_argument("--pcap", type=Path, default=DEFAULT_PCAP)
    parser.add_argument("--protocol-log", type=Path, default=DEFAULT_PROTOCOL_LOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--live",
        action="store_true",
        help="request live replay (currently refused; no USB transport is implemented)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_replay(args.source, args.pcap, args.protocol_log, args.output)
    except ReplayBuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = {
        "path": _display_path(args.output),
        "entry_count": manifest["entry_count"],
        "source": manifest["source"],
        "mode": "live-refused" if args.live else "dry-run",
    }
    print(json.dumps(summary, indent=2))
    if args.live:
        print(
            "error: --live was explicit, but live USB replay is not implemented; no USB data was sent",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
