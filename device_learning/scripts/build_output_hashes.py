#!/usr/bin/env python3
"""Compute SHA256 hashes of generated outputs for reproducibility tracking."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTPUTS = [
    "EvidenceLedger.json",
    "coverage.json",
    "bridge_matrix.json",
    "STATIC_REPORT.md",
    "CONFIRMED_REPORT.md",
    "BLOCKED_REPORT.md",
    "BRIDGE_REPORT.md",
    "ARCHITECTURE.md",
    "IDENTIFIER_INDEX.md",
    "manifests/evidence_summary.json",
    "manifests/completion_status.json",
    "manifests/catalog_integrity.json",
    "manifests/sensitive_audit.json",
    "manifests/frame_summary.json",
    "manifests/pending_index.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    entries = []
    for rel in OUTPUTS:
        path = ROOT / rel
        if path.exists():
            entries.append({"path": rel, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})

    combined = hashlib.sha256()
    for e in sorted(entries, key=lambda x: x["path"]):
        combined.update(e["sha256"].encode())

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_count": len(entries),
        "combined_sha256": combined.hexdigest(),
        "outputs": entries,
        "boundary": "Hashes of generated artifacts; inputs see file_hashes.json",
    }
    out = ROOT / "manifests" / "output_hashes.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output_count": len(entries), "combined_sha256": meta["combined_sha256"][:16] + "..."}, indent=2))


if __name__ == "__main__":
    main()
