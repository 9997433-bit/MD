"""Sample manifest accuracy tests (subagent #3 findings)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_all_samples_have_mea_type():
    data = json.loads((ROOT / "manifests" / "sample_manifest.json").read_text(encoding="utf-8"))
    for s in data["samples"]:
        assert s["mea_type_choosing"] is not None, s["file"]
        assert s["field_count"] == 191, s["file"]


def test_timebase_samples_no_linear_err_data():
    data = json.loads((ROOT / "manifests" / "sample_manifest.json").read_text(encoding="utf-8"))
    for name in ("Sample.LTB", "Sample.ATB", "Sample.STB"):
        s = next(x for x in data["samples"] if x["file"] == name)
        assert s["has_linear_err"] is False
        assert s.get("has_timebase_raw") is True or name == "Sample.STB"


def test_lda_mea_type_12():
    data = json.loads((ROOT / "manifests" / "sample_manifest.json").read_text(encoding="utf-8"))
    lda = next(x for x in data["samples"] if x["file"] == "Sample.LDA")
    assert lda["mea_type_choosing"] == 12
