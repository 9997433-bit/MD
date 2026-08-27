"""Tests for catalog integrity and sensitive token audit."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_integrity_ok():
    data = json.loads((ROOT / "manifests" / "catalog_integrity.json").read_text())
    assert data["ok"] is True
    assert data["entry_count"] >= 237
    assert data["duplicate_count"] == 0


def test_sensitive_audit_clean():
    data = json.loads((ROOT / "manifests" / "sensitive_audit.json").read_text())
    assert data["ok"] is True
    assert data["finding_count"] == 0


def test_evidence_summary():
    data = json.loads((ROOT / "manifests" / "evidence_summary.json").read_text())
    assert data["identifiers"] >= 237
    assert data["blocked"] >= 90
    assert data["bitstream"]["idcode"] == "0x01414093"
    assert data["catalog_integrity_ok"] is True


def test_blocked_report_exists():
    path = ROOT / "BLOCKED_REPORT.md"
    assert path.exists()
    text = path.read_text()
    assert "missing" in text
    assert "FW-MCU-CORE-IMAGE" in text
