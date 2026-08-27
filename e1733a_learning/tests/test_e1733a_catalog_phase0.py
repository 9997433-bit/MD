"""Phase 0 tests: manifests and ledger skeleton."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_files_exist():
    p = ROOT / "manifests" / "manifest_files.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["file_count"] >= 50


def test_pe_exports_exist():
    data = json.loads((ROOT / "manifests" / "pe_exports.json").read_text(encoding="utf-8"))
    assert "E1735A.dll" in data
    assert "E1735ACore_ProcessRawData" in data["E1735ACore.dll"]["exports"]


def test_setup_constants_parsed():
    data = json.loads((ROOT / "manifests" / "setup_constants.json").read_text(encoding="utf-8"))
    assert data["count"] > 100


def test_evidence_ledger_phases():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    assert set(data["phases_completed"]) >= {"0", "A", "B", "C", "D"}
