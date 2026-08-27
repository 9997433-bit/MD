#!/usr/bin/env python3
"""Update phase_c/CHECKLIST.json from experiment logs directory."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "phase_c" / "CHECKLIST.json"
LOGS = ROOT / "phase_c" / "logs"


def main() -> None:
    data = json.loads(CHECKLIST.read_text(encoding="utf-8"))
    log_files = list(LOGS.glob("*.json")) if LOGS.exists() else []
    logged_ids = set()
    for lf in log_files:
        try:
            logged_ids.add(json.loads(lf.read_text(encoding="utf-8")).get("experiment_id", ""))
        except json.JSONDecodeError:
            pass

    for task in data.get("tasks", []):
        exp = task.get("experiment")
        if exp and exp in logged_ids:
            task["done"] = True
        elif task.get("id") == "C6":
            task["done"] = len(log_files) > 0

    done_count = sum(1 for t in data["tasks"] if t.get("done"))
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["done_count"] = done_count
    data["total_count"] = len(data["tasks"])
    data["status"] = "complete" if done_count == len(data["tasks"]) else ("in_progress" if done_count else "not_started")

    CHECKLIST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"done_count": done_count, "status": data["status"]}, indent=2))


if __name__ == "__main__":
    main()
