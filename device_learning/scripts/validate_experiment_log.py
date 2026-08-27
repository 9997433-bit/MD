#!/usr/bin/env python3
"""Validate phase C experiment log JSON files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "phase_c" / "logs"
OUT = ROOT / "manifests" / "experiment_validation.json"

VALID_CONCLUSION = {"confirmed", "refuted", "inconclusive"}
VALID_CONFIDENCE = {"unknown", "hypothesis", "confirmed"}


def validate_file(path: Path) -> dict:
    issues: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"file": path.name, "valid": False, "issues": [str(exc)]}

    for key in ("experiment_id", "date", "observation", "conclusion"):
        if not data.get(key):
            issues.append(f"missing {key}")
    if data.get("conclusion") not in VALID_CONCLUSION:
        issues.append("invalid conclusion")
    if data.get("confidence") and data.get("confidence") not in VALID_CONFIDENCE:
        issues.append("invalid confidence")

    return {
        "file": path.name,
        "experiment_id": data.get("experiment_id"),
        "valid": not issues,
        "issues": issues,
        "conclusion": data.get("conclusion"),
    }


def main() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in LOGS.glob("*.json") if p.name != "README.md")
    results = [validate_file(p) for p in files]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "log_count": len(results),
        "valid_count": sum(1 for r in results if r["valid"]),
        "files": results,
        "boundary": "Validation only; does not auto-upgrade catalog entries",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"log_count": report["log_count"], "valid_count": report["valid_count"]}, indent=2))


if __name__ == "__main__":
    main()
