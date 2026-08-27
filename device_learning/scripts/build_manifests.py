#!/usr/bin/env python3
"""Build file hash and input-file manifests for the device_learning corpus.

Uses neutral naming; does not reference any specific product model.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_DIR = ROOT / "manifests"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_inputs() -> list[Path]:
    inputs: list[Path] = []
    firmware = ROOT / "firmware" / "device.bit"
    if firmware.is_file():
        inputs.append(firmware)
    photos = sorted((ROOT / "hardware" / "photos").glob("*.jpg"))
    inputs.extend(photos)
    return inputs


def build_entry(path: Path) -> dict:
    stat = path.stat()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": stat.st_size,
        "sha256": sha256_of(path),
    }


def main() -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    inputs = collect_inputs()
    entries = [build_entry(p) for p in inputs]
    generated_at = datetime.now(timezone.utc).isoformat()

    file_hashes = {
        "generated_at": generated_at,
        "source_dir": ROOT.as_posix(),
        "file_count": len(entries),
        "files": entries,
    }
    (MANIFEST_DIR / "file_hashes.json").write_text(
        json.dumps(file_hashes, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    manifest_files = {
        "generated_at": generated_at,
        "source_dir": ROOT.as_posix(),
        "file_count": len(entries),
        "files": [
            {"path": e["path"], "size_bytes": e["size_bytes"]} for e in entries
        ],
    }
    (MANIFEST_DIR / "manifest_files.json").write_text(
        json.dumps(manifest_files, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"file_hashes.json: {len(entries)} entries")
    print(f"manifest_files.json: {len(entries)} entries")


if __name__ == "__main__":
    main()
