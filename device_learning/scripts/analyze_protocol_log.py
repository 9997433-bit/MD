#!/usr/bin/env python3
"""Validate and summarize phase_b/captures/protocol_log.json when present."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "phase_b" / "captures" / "protocol_log.json"
OUT = ROOT / "manifests" / "protocol_log_meta.json"

REQUIRED_META = ("capture_source", "capture_file", "captured_at")
VALID_DIRECTION = {"host_to_device", "device_to_host"}
VALID_TRANSFER = {"control", "bulk", "interrupt", "isochronous"}
VALID_CONFIDENCE = {"unknown", "hypothesis", "confirmed"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(data: dict) -> dict:
    issues: list[str] = []
    meta = data.get("meta") or {}
    for key in REQUIRED_META:
        if not meta.get(key):
            issues.append(f"meta.{key} empty")

    commands = data.get("commands") or []
    if not commands:
        issues.append("commands empty")
    else:
        for i, cmd in enumerate(commands):
            if cmd.get("direction") not in VALID_DIRECTION:
                issues.append(f"commands[{i}].direction invalid")
            if cmd.get("transfer_type") not in VALID_TRANSFER:
                issues.append(f"commands[{i}].transfer_type invalid")
            conf = cmd.get("confidence", "unknown")
            if conf not in VALID_CONFIDENCE:
                issues.append(f"commands[{i}].confidence invalid")

    unresolved = data.get("unresolved") or []
    return {
        "command_count": len(commands),
        "unresolved_count": len(unresolved),
        "meta_present": {k: bool(meta.get(k)) for k in REQUIRED_META},
        "valid": not issues,
        "issues": issues,
    }


def main() -> None:
    if not LOG.exists():
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "missing",
            "path": str(LOG.relative_to(ROOT)),
            "boundary": "Optional; copy phase_b/templates/protocol_log_template.json after capture",
        }
    else:
        raw = LOG.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            meta = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "invalid_json",
                "error": str(exc),
            }
        else:
            v = validate(data)
            meta = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "observed" if v["valid"] else "invalid",
                "path": str(LOG.relative_to(ROOT)),
                "size_bytes": LOG.stat().st_size,
                "sha256": sha256_file(LOG),
                **v,
                "boundary": "Human-curated log; does not auto-upgrade PROTO-* without ledger review",
            }

    OUT.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
