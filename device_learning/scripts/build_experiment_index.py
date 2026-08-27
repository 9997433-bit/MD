#!/usr/bin/env python3
"""Index phase C experiment logs for ledger manifests."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "phase_c" / "logs"
OUT = ROOT / "manifests" / "experiment_index.json"


def main() -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    entries = []
    for path in sorted(LOGS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        entries.append(
            {
                "file": path.name,
                "experiment_id": data.get("experiment_id"),
                "date": data.get("date"),
                "conclusion": data.get("conclusion"),
                "identifiers_proposed_upgrade": data.get("identifiers_proposed_upgrade", []),
            }
        )

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entry_count": len(entries),
        "experiments": entries,
        "boundary": "Index only; catalog upgrades require human review",
    }
    OUT.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"entry_count": index["entry_count"]}, indent=2))


if __name__ == "__main__":
    main()
