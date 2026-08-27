"""English.csv gap manifest tests."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_english_gaps_file_exists():
    p = ROOT / "manifests" / "english_string_gaps.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["ledger_has_string_id_anchors"] is False
    assert len(data["gap_blocks"]) >= 5


def test_forced_null_reminders_present():
    data = json.loads((ROOT / "manifests" / "english_string_gaps.json").read_text(encoding="utf-8"))
    assert any("Edlen" in r or "Wavelength" in r for r in data["forced_null_reminders"])
