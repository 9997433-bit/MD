"""Test file hash manifest consistency."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_bitstream_hash():
    bit = ROOT / "firmware" / "device.bit"
    assert bit.exists()
    h = sha256_file(bit)
    assert h == "63cd3874297407bceedb524909d919dd35ba8a16639573a1af81721aed4fc3f5"


def test_manifest_hashes_match():
    manifest = ROOT / "manifests" / "file_hashes.json"
    if not manifest.exists():
        return  # skip if ledger not generated yet
    data = json.loads(manifest.read_text())
    for entry in data["files"]:
        p = ROOT / entry["path"]
        assert p.exists(), entry["path"]
        assert sha256_file(p) == entry["sha256"], entry["path"]


def test_manifest_file_count():
    manifest = json.loads((ROOT / "manifests" / "file_hashes.json").read_text())
    assert manifest["file_count"] == 11


def test_photo_count():
    photos = list((ROOT / "hardware" / "photos").glob("*.jpg"))
    assert len(photos) == 10
