#!/usr/bin/env python3
"""Pre-flight validation for phase B capture files (no ledger side effects)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from eeprom_source import is_synthetic_dump  # noqa: E402
from pcap_source import is_synthetic_pcap  # noqa: E402

CAPTURES = ROOT / "phase_b" / "captures"
EXPECTED = {
    "eeprom.bin": {"size": 8192, "label": "24LC64 全片镜像"},
    "usb_enum.pcapng": {"label": "USB 枚举抓包"},
    "usb_session.pcapng": {"label": "USB 工作/配置抓包"},
}
PCAP_MAGIC = {
    b"\xd4\xc3\xb2\xa1": "pcap_le",
    b"\xa1\xb2\xc3\xd4": "pcap_be",
    b"\x0a\x0d\x0d\x0a": "pcapng",
}


def sniff_magic(path: Path) -> str:
    head = path.read_bytes()[:4]
    return PCAP_MAGIC.get(head, "unknown")


def check_file(name: str, spec: dict) -> dict:
    path = CAPTURES / name
    row: dict = {"name": name, "label": spec["label"], "present": path.is_file()}
    if not row["present"]:
        row["ok"] = False
        row["issue"] = "missing"
        return row
    row["size_bytes"] = path.stat().st_size
    if name == "eeprom.bin":
        data = path.read_bytes()
        row["is_synthetic_fixture"] = is_synthetic_dump(data)
        if row["is_synthetic_fixture"]:
            row["ok"] = False
            row["issue"] = "SHA-256 matches synthetic fixture — replace with real device dump"
            return row
    if "size" in spec and row["size_bytes"] != spec["size"]:
        row["ok"] = False
        row["issue"] = f"expected {spec['size']} bytes, got {row['size_bytes']}"
        return row
    if name.endswith((".pcap", ".pcapng")):
        magic = sniff_magic(path)
        row["magic"] = magic
        if magic == "unknown":
            row["ok"] = False
            row["issue"] = "unrecognized pcap/pcapng magic"
            return row
        if is_synthetic_pcap(path.read_bytes()):
            row["is_synthetic_fixture"] = True
            row["ok"] = False
            row["issue"] = "SHA-256 matches synthetic fixture — replace with real capture"
            return row
    row["ok"] = True
    return row


def main() -> int:
    CAPTURES.mkdir(parents=True, exist_ok=True)
    checks = [check_file(name, spec) for name, spec in EXPECTED.items()]
    optional = CAPTURES / "protocol_log.json"
    if optional.is_file():
        try:
            payload = json.loads(optional.read_text(encoding="utf-8"))
            entries = len(payload.get("commands", payload))
        except json.JSONDecodeError:
            entries = None
        checks.append(
            {
                "name": "protocol_log.json",
                "label": "手工协议记录（可选）",
                "present": True,
                "ok": entries is not None,
                "protocol_entries": entries,
                "issue": None if entries is not None else "invalid JSON",
            }
        )

    ready = all(c["ok"] for c in checks if c["name"] != "protocol_log.json")
    partial = any(c["present"] for c in checks)
    synthetic_only = any(c.get("is_synthetic_fixture") for c in checks)

    report = {
        "captures_dir": str(CAPTURES.relative_to(ROOT)),
        "checks": checks,
        "ready_for_phase_b": ready,
        "partial_captures": partial and not ready,
        "synthetic_fixture_detected": synthetic_only,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if synthetic_only:
        print("\n警告: 检测到合成夹具，不能作为实机证据。", file=sys.stderr)
        return 3
    if not partial:
        print("\n提示: 尚无采集文件。见 HARDWARE_HANDOFF.md", file=sys.stderr)
        return 1
    if not ready:
        print("\n提示: 部分文件缺失或格式不符，见上方 checks。", file=sys.stderr)
        return 2
    print("\n采集文件预检通过，可运行 make phase-b")
    return 0


if __name__ == "__main__":
    sys.exit(main())
