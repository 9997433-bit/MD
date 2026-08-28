"""Assert command-plane framing taxonomy when session capture is present."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"
TAXONOMY = ROOT / "manifests" / "usb_command_taxonomy.json"


@pytest.mark.skipif(not SESSION.exists(), reason="phase_b/captures/usb_session.pcapng missing")
def test_usb_command_taxonomy_framing_100():
    if not TAXONOMY.exists():
        return
    data = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    if data.get("status") != "hypothesis":
        return
    framing = data["framing_hypothesis"]
    assert framing["ep01_out"]["both_ratio"] == 1.0
    assert framing["ep81_in"]["both_ratio"] == 1.0
    assert len(data["out_opcodes"]) >= 1
    assert data["in_status_bytes_top"][0]["value"] == "0x00"
