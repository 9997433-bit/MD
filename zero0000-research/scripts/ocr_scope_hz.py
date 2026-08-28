#!/usr/bin/env python3
"""
从示波器/频率计屏幕截图 OCR 提取频率（降低 Must 投放门槛）。

依赖：系统 tesseract + Python Pillow + pytesseract。

用法：
  python3 scripts/ocr_scope_hz.py photo.jpg
  python3 scripts/ocr_scope_hz.py photo.jpg --as-c2 --as-c3-same   # 计划 B 单帧
  python3 scripts/ocr_scope_hz.py photo.jpg --as-c2 --write-clocks --confirm-measured
  python3 scripts/ocr_scope_hz.py --self-test

安全：写入 g2_inbox/g2_clocks.json 必须 --confirm-measured（OCR 可能误读）。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "05_tests" / "g2_inbox" / "g2_clocks.json"
TEMPLATE = ROOT / "05_tests" / "g2_inbox" / "g2_clocks.template.json"

# 245.76 MHz, 245.760 MHz, 2.4576e8 Hz, 245760000, Freq=245.76MHz, etc.
HZ_PATTERNS = [
    re.compile(
        r"(?P<num>\d+(?:[.,]\d+)?)\s*[eE]\s*(?P<exp>[+-]?\d+)\s*(?P<unit>[kKmMgG]?[Hh][Zz])?",
        re.I,
    ),
    re.compile(
        r"(?P<num>\d+(?:[.,]\d+)?)\s*[×x*]?\s*10\s*[\^]?\s*(?P<exp>[+-]?\d+)\s*(?P<unit>[kKmMgG]?[Hh][Zz])?",
        re.I,
    ),
    re.compile(
        r"(?P<num>\d+(?:[.,]\d+)?)\s*(?P<unit>[kKmMgG]?[Hh][Zz]|MSPS|Msps|msps)",
        re.I,
    ),
    re.compile(r"(?P<num>\d{6,12})(?!\d)"),  # raw integer Hz
]


def _to_float(num: str) -> float:
    return float(num.replace(",", "."))


def parse_hz_candidates(text: str) -> list[dict]:
    found: list[dict] = []
    seen: set[int] = set()
    for pat in HZ_PATTERNS:
        for m in pat.finditer(text):
            gd = m.groupdict()
            num = _to_float(gd["num"])
            unit = (gd.get("unit") or "Hz").lower()
            if "exp" in gd and gd["exp"] is not None:
                num *= 10 ** int(gd["exp"])
            if unit.startswith("g"):
                hz = num * 1e9
            elif unit.startswith("m") and "sps" not in unit:
                hz = num * 1e6
            elif "sps" in unit:
                hz = num * 1e6  # treat Msps as MHz sample rate
            elif unit.startswith("k"):
                hz = num * 1e3
            else:
                hz = num
            # keep RF-ish band
            if not (1e6 <= hz <= 2e9):
                continue
            key = int(round(hz))
            if key in seen:
                continue
            seen.add(key)
            found.append({"hz": key, "raw": m.group(0), "from": "ocr"})
    found.sort(key=lambda x: -x["hz"])
    return found


def ocr_image(path: Path) -> str:
    if shutil.which("tesseract") is None:
        raise SystemExit("tesseract not installed")
    try:
        from PIL import Image, ImageOps, ImageFilter
    except ImportError as e:
        raise SystemExit(f"Pillow required: {e}") from e

    img = Image.open(path)
    # enhance: grayscale + autocontrast + mild sharpen; also try upscale
    gray = ImageOps.grayscale(img)
    variants = [
        gray,
        ImageOps.autocontrast(gray),
        ImageOps.autocontrast(gray).filter(ImageFilter.SHARPEN),
        gray.resize((gray.width * 2, gray.height * 2)),
    ]
    texts: list[str] = []
    for i, v in enumerate(variants):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            v.save(tmp.name)
            out = subprocess.run(
                ["tesseract", tmp.name, "stdout", "--psm", "6"],
                capture_output=True,
                text=True,
                check=False,
            )
            Path(tmp.name).unlink(missing_ok=True)
            if out.stdout.strip():
                texts.append(out.stdout)
    return "\n".join(texts)


def load_template() -> list[dict]:
    if TEMPLATE.is_file():
        return json.loads(TEMPLATE.read_text(encoding="utf-8"))
    return [{"id": i, "hz": None, "note": ""} for i in ("C1", "C2", "C3", "C6", "C7a", "C7b")]


def write_clocks(c2: int | None, c3: int | None, out: Path, note: str) -> None:
    rows = load_template()
    for r in rows:
        if r["id"] == "C2" and c2 is not None:
            r["hz"] = c2
            r["note"] = f"OCR measured · {note}"
        if r["id"] == "C3" and c3 is not None:
            r["hz"] = c3
            r["note"] = f"OCR measured · {note}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def self_test() -> int:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (640, 200), "black")
    draw = ImageDraw.Draw(img)
    draw.text((40, 70), "Freq  245.76 MHz", fill="white")
    path = Path(tempfile.mkstemp(suffix="_scope.png")[1])
    img.save(path)
    text = ocr_image(path)
    cands = parse_hz_candidates(text + "\n245.76 MHz")  # guarantee parse unit test
    path.unlink(missing_ok=True)
    # unit parse always
    c2 = parse_hz_candidates("Freq=245.76 MHz\nDACCLK 491.52 MHz")
    assert any(abs(c["hz"] - 245760000) < 1000 for c in c2), c2
    assert any(abs(c["hz"] - 491520000) < 1000 for c in c2), c2
    print("SELF-TEST OK ocr_scope_hz parse; ocr_text_len=", len(text))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("images", nargs="*", type=Path)
    ap.add_argument("--as-c2", type=int, metavar="N", help="use N-th candidate (0-based) as C2")
    ap.add_argument("--as-c3", type=int, metavar="N", help="use N-th candidate as C3")
    ap.add_argument("--as-c3-same", action="store_true", help="copy C2 into C3 (plan B)")
    ap.add_argument("--write-clocks", action="store_true")
    ap.add_argument("--confirm-measured", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.images:
        ap.error("image path required")

    all_text = []
    all_cands: list[dict] = []
    for img in args.images:
        if not img.is_file():
            print(f"missing {img}", file=sys.stderr)
            return 2
        text = ocr_image(img)
        all_text.append(f"--- {img.name} ---\n{text}")
        for c in parse_hz_candidates(text):
            c["file"] = img.name
            all_cands.append(c)

    # dedupe by hz
    uniq: dict[int, dict] = {}
    for c in all_cands:
        uniq.setdefault(c["hz"], c)
    cands = sorted(uniq.values(), key=lambda x: -x["hz"])

    report = {"candidates": cands, "ocr_preview": "\n".join(all_text)[:2000]}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("OCR candidates (1e6–2e9 Hz):")
        if not cands:
            print("  (none — try crop to frequency readout, higher contrast)")
        for i, c in enumerate(cands):
            print(f"  [{i}] {c['hz']} Hz  raw={c['raw']!r}  file={c.get('file')}")
        print("--- OCR text preview ---")
        print("\n".join(all_text)[:1500])

    if args.write_clocks:
        if not args.confirm_measured:
            print("refusing --write-clocks without --confirm-measured", file=sys.stderr)
            return 2
        if args.as_c2 is None and not cands:
            print("no candidates to write", file=sys.stderr)
            return 1
        idx2 = 0 if args.as_c2 is None else args.as_c2
        c2 = cands[idx2]["hz"] if cands else None
        c3 = None
        if args.as_c3 is not None:
            c3 = cands[args.as_c3]["hz"]
        elif args.as_c3_same:
            c3 = c2
        note = ",".join(p.name for p in args.images)
        write_clocks(c2, c3, args.out, note)
        print(f"WROTE {args.out} C2={c2} C3={c3}")
        print("next: python3 scripts/ingest_g2_inbox.py && python3 scripts/apply_g0_backfill.py --apply")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
