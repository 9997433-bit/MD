"""Parallel-artifact sanity checks.

阶段性并行产物：docs/ 与 manifests/ 中计划文件若已生成则必须格式合法；
catalog_spec_sync 的 SPEC id 集合必须无重复且包含核心条目。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalogs.catalog_spec_sync import entry_ids as spec_ids  # noqa: E402

# 计划中的并行产物（可能尚未全部生成）。
PLANNED_JSON = [
    ROOT / "manifests" / "bitstream_meta.json",
    ROOT / "manifests" / "file_hashes.json",
    ROOT / "manifests" / "firmware_meta.json",
    ROOT / "manifests" / "manifest_files.json",
    ROOT / "manifests" / "photo_index.json",
    ROOT / "manifests" / "system_map.json",
    ROOT / "EvidenceLedger.json",
    ROOT / "coverage.json",
    ROOT / "bridge_matrix.json",
]
PLANNED_DOCS = [
    ROOT / "docs" / "PHASE_PLAN.md",
]


def test_dirs_exist():
    assert (ROOT / "docs").is_dir()
    assert (ROOT / "manifests").is_dir()


@pytest.mark.parametrize("path", PLANNED_JSON, ids=lambda p: p.name)
def test_planned_json_parseable_if_present(path: Path):
    if not path.is_file():
        pytest.skip(f"{path.name} not generated yet")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, (dict, list))


@pytest.mark.parametrize("path", PLANNED_DOCS, ids=lambda p: p.name)
def test_planned_docs_nonempty_if_present(path: Path):
    if not path.is_file():
        pytest.skip(f"{path.name} not generated yet")
    assert path.read_text(encoding="utf-8").strip()


def test_spec_ids_unique_and_core_present():
    ids = spec_ids()
    assert len(ids) == len(set(ids)), "duplicate SPEC ids"
    assert "SPEC-ADC-16" in ids


def test_spec_ids_new_parallel_entries():
    ids = set(spec_ids())
    assert {
        "SPEC-FIFO-SHARED-DEPTH",
        "SPEC-DIFF-16",
        "SPEC-RANGE-LIST",
        "SPEC-MIN-RATE-NONE",
        "SPEC-OEM-VARIANT",
    } <= ids
