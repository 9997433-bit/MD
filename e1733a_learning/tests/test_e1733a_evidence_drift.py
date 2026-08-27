"""Bridge matrix and stop condition drift tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_forced_null_bridges():
    data = json.loads((ROOT / "bridge_matrix.json").read_text(encoding="utf-8"))
    assert len(data["forced_null_bridges"]) >= 7
    for cell in data["cells"].values():
        assert cell["proven_bridge"] is None


def test_stop_condition_flags():
    data = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    sc = data["stop_condition"]
    assert sc["forced_null_bridges_intact"] is True
    assert sc["forbidden_writers_intact"] is True
    assert "目录完整" in sc["conclusion"]


def test_fmt_ltb_velocity_null():
    data = json.loads((ROOT / "EvidenceLedger.json").read_text(encoding="utf-8"))
    e = next(x for x in data["catalogs"]["formats"] if x["identifier"] == "FMT-LTB-VELOCITY-BRIDGE")
    assert e.get("proven_bridge") is None
