#!/usr/bin/env python3
"""
把示波器/频率计读数写成 g2_inbox/g2_clocks.json（缩短 Must-1 投放）。

安全：
  - 写入默认 inbox 根目录时必须 --confirm-measured（禁止把先验当实测）
  - 禁止输出路径含 demo/example
  - 值须为有限正数 Hz

用法：
  python3 scripts/mk_g2_clocks.py --c2 245760000 --c3 245760000 --confirm-measured
  python3 scripts/mk_g2_clocks.py --c2 245.76e6 --dry-run
  python3 scripts/mk_g2_clocks.py --from-csv readings.csv --confirm-measured
  python3 scripts/mk_g2_clocks.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "05_tests" / "g2_inbox" / "g2_clocks.json"
TEMPLATE = ROOT / "05_tests" / "g2_inbox" / "g2_clocks.template.json"

IDS = ("C1", "C2", "C3", "C6", "C7a", "C7b")


def parse_hz(text: str | None) -> float | None:
    if text is None or str(text).strip() == "":
        return None
    v = float(text)
    if not (v > 0) or v != v:  # NaN
        raise ValueError(f"hz must be finite >0, got {text!r}")
    return v


def load_template() -> list[dict]:
    if TEMPLATE.is_file():
        return json.loads(TEMPLATE.read_text(encoding="utf-8"))
    return [{"id": i, "hz": None, "note": ""} for i in IDS]


def apply_overrides(rows: list[dict], overrides: dict[str, float | None]) -> list[dict]:
    by_id = {r["id"]: dict(r) for r in rows}
    for cid, hz in overrides.items():
        if cid not in by_id:
            by_id[cid] = {"id": cid, "hz": None, "note": ""}
        by_id[cid]["hz"] = None if hz is None else int(round(hz))
        if hz is not None and "measured" not in str(by_id[cid].get("note", "")).lower():
            note = by_id[cid].get("note") or cid
            by_id[cid]["note"] = f"{note} · measured"
    # preserve template order then extras
    ordered = []
    seen = set()
    for r in rows:
        ordered.append(by_id[r["id"]])
        seen.add(r["id"])
    for cid in IDS:
        if cid not in seen and cid in by_id:
            ordered.append(by_id[cid])
            seen.add(cid)
    for cid, row in by_id.items():
        if cid not in seen:
            ordered.append(row)
    return ordered


def from_csv(path: Path) -> dict[str, float | None]:
    """CSV columns: id,hz  (hz may be 245.76e6 or 245760000)."""
    out: dict[str, float | None] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "id" not in reader.fieldnames:
            raise SystemExit("CSV needs header with id,hz")
        for row in reader:
            cid = (row.get("id") or "").strip()
            if not cid:
                continue
            out[cid] = parse_hz(row.get("hz"))
    return out


def self_test() -> int:
    rows = apply_overrides(
        load_template(),
        {"C2": parse_hz("245.76e6"), "C3": parse_hz("245760000")},
    )
    by = {r["id"]: r["hz"] for r in rows}
    if by.get("C2") != 245760000 or by.get("C3") != 245760000:
        print("SELF-TEST FAILED", by, file=sys.stderr)
        return 1
    filled = [r for r in rows if r.get("hz") is not None]
    if len(filled) != 2:
        print("SELF-TEST FAILED fill count", file=sys.stderr)
        return 1
    print("SELF-TEST OK mk_g2_clocks")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--c1", help="X1 VCXO Hz")
    ap.add_argument("--c2", help="ADC CLKP Hz")
    ap.add_argument("--c3", help="DAC DACCLK Hz")
    ap.add_argument("--c6", help="DAC DATACLK Hz")
    ap.add_argument("--c7a", help="X2 100M Hz")
    ap.add_argument("--c7b", help="X3 200M Hz")
    ap.add_argument("--from-csv", type=Path, help="CSV with id,hz columns")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--confirm-measured",
        action="store_true",
        help="required when writing into g2_inbox root (not examples/)",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    overrides: dict[str, float | None] = {}
    if args.from_csv:
        overrides.update(from_csv(args.from_csv))
    for cid, raw in (
        ("C1", args.c1),
        ("C2", args.c2),
        ("C3", args.c3),
        ("C6", args.c6),
        ("C7a", args.c7a),
        ("C7b", args.c7b),
    ):
        if raw is not None:
            overrides[cid] = parse_hz(raw)

    if not overrides:
        print("provide --c2/--c3/... or --from-csv", file=sys.stderr)
        return 2

    rows = apply_overrides(load_template(), overrides)
    filled = [r["id"] for r in rows if r.get("hz") is not None]
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    out = args.out.resolve()
    out_l = str(out).lower()
    if "demo" in out_l or "example" in out_l:
        print(f"refusing demo/example path: {out}", file=sys.stderr)
        return 2

    inbox_root = (ROOT / "05_tests" / "g2_inbox").resolve()
    writing_inbox = out.parent == inbox_root and out.name == "g2_clocks.json"
    if writing_inbox and not args.confirm_measured and not args.dry_run:
        print(
            "refusing to write measured clocks into g2_inbox without "
            "--confirm-measured (do not fill priors as facts)",
            file=sys.stderr,
        )
        return 2

    print(f"filled={filled}")
    if args.dry_run:
        print(text)
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"WROTE {out}")
    print("next: python3 scripts/ingest_g2_inbox.py && python3 scripts/apply_g0_backfill.py --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
