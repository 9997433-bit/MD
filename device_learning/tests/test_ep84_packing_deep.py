"""Tests for EP84 deep packing / EP01 arm sequence analyzer."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SESSION = ROOT / "phase_b" / "captures" / "usb_session.pcapng"
OUT_PACK = ROOT / "manifests" / "ep84_packing_deep.json"
OUT_ARM = ROOT / "manifests" / "ep01_stream_arm_sequence.json"

BANNED = "".join(chr(c) for c in (0x34, 0x34, 0x33, 0x31))


def test_analyze_ep84_packing_deep_runs():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "analyze_ep84_packing_deep.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert OUT_PACK.exists()
    assert OUT_ARM.exists()
    pack = json.loads(OUT_PACK.read_text(encoding="utf-8"))
    arm = json.loads(OUT_ARM.read_text(encoding="utf-8"))
    assert pack.get("status") in {"hypothesis_only", "missing", "hypothesis"}
    assert "confirmed" not in json.dumps(pack.get("top_hypothesis", {})).lower() or pack.get(
        "top_hypothesis", {}
    ).get("confidence") != "confirmed"
    assert all(h.get("confidence") != "confirmed" for h in pack.get("hypotheses_ranked", []))
    assert BANNED not in OUT_PACK.read_text(encoding="utf-8")
    assert BANNED not in OUT_ARM.read_text(encoding="utf-8")
    if SESSION.exists() and pack.get("status") == "hypothesis_only":
        assert pack["ep84_payload_count"] >= 1
        assert pack["top_hypothesis"]["confidence"] in {"candidate", "hypothesis"}
        assert arm.get("ep84_burst_count", 0) >= 1


def test_run_phase_b_wires_packing_deep():
    text = (SCRIPTS / "run_phase_b.py").read_text(encoding="utf-8")
    assert "analyze_ep84_packing_deep.py" in text
