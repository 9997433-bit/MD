#!/usr/bin/env python3
"""Update phase_b/CHECKLIST.json task done flags from captures directory."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "phase_b" / "CHECKLIST.json"
CAPTURES = ROOT / "phase_b" / "captures"
ANALYSIS = ROOT / "phase_b" / "analysis"


def artifact_exists(rel: str | None) -> bool:
    if not rel:
        return False
    return (ROOT / rel).is_file()


def main() -> None:
    data = json.loads(CHECKLIST.read_text(encoding="utf-8"))
    for task in data.get("tasks", []):
        art = task.get("artifact")
        if art:
            task["done"] = artifact_exists(art)
        if task.get("id") == "B5":
            task["done"] = artifact_exists("phase_b/captures/eeprom.bin") or any(
                CAPTURES.glob("*.pcapng")
            )

    done_count = sum(1 for t in data["tasks"] if t.get("done"))
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["done_count"] = done_count
    data["total_count"] = len(data["tasks"])
    data["status"] = "complete" if done_count == len(data["tasks"]) else ("in_progress" if done_count else "not_started")

    CHECKLIST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"done_count": done_count, "status": data["status"]}, indent=2))


if __name__ == "__main__":
    main()
