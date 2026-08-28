#!/usr/bin/env python3
"""
Ingest G2 captures from 05_tests/g2_inbox/ → decode + mode infer + report.

Does NOT modify G0 grades automatically (human must paste with hashes).
Exits 2 if inbox has no usable clocks.json / spi csv.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INBOX = ROOT / "05_tests" / "g2_inbox"
SCRIPTS = ROOT / "scripts"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inbox", type=Path, default=DEFAULT_INBOX)
    ap.add_argument("--sclk", default=None)
    ap.add_argument("--mosi", default=None)
    ap.add_argument("--cs-adc", default=None)
    ap.add_argument("--cs-dac", default=None)
    ap.add_argument("--cs-cdce", default=None)
    ap.add_argument(
        "--demo",
        action="store_true",
        help="run Conserviss synthetic demo into _derived/demo_* (NOT for G0 backfill)",
    )
    args = ap.parse_args()
    inbox: Path = args.inbox.resolve()

    if args.demo:
        return run_demo(inbox)

    return run_ingest(inbox, args)


def run_demo(inbox: Path) -> int:
    """End-to-end pipeline with synthetic Conserviss + plan-B clocks. Never touches G0."""
    demo_dir = inbox / "_derived" / "demo_inbox"
    if demo_dir.exists():
        for p in demo_dir.iterdir():
            if p.is_file():
                p.unlink()
    demo_dir.mkdir(parents=True, exist_ok=True)
    clocks = demo_dir / "g2_clocks.json"
    clocks.write_text(
        json.dumps(
            [
                {"id": "C2", "hz": 245760000, "note": "DEMO Conserviss plan B"},
                {"id": "C3", "hz": 245760000, "note": "DEMO"},
                {"id": "C6", "hz": 122880000, "note": "DEMO DATACLK"},
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    csv_path = demo_dir / "spi_capture.conserviss_min.example.csv"
    r = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "decode_spi_capture.py"),
            "--write-conserviss-example",
            str(csv_path),
        ],
        cwd=ROOT,
    )
    if r.returncode != 0:
        return r.returncode
    # Isolate reports under demo_dir
    class Args:
        sclk = mosi = cs_adc = cs_dac = cs_cdce = None

    code = run_ingest(demo_dir, Args(), demo_banner=True)
    print(
        "DEMO DONE — outputs under g2_inbox/_derived/demo_inbox/ ; "
        "DO NOT paste into G0 (synthetic).",
        file=sys.stderr,
    )
    return code


def run_ocr_hint(inbox: Path, images: list[Path], out_dir: Path) -> int:
    """OCR scope photos → candidate Hz; do NOT write g2_clocks without confirm."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SCRIPTS / "ocr_scope_hz.py"),
        *[str(p) for p in images],
        "--json",
    ]
    print("RUN", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    report_path = out_dir / "ocr_scope_candidates.json"
    md_path = (
        ROOT / "05_tests" / "G2_OCR候选.md"
        if inbox == DEFAULT_INBOX.resolve()
        else inbox / "G2_OCR候选.md"
    )
    blob: dict = {}
    if r.returncode == 0 and r.stdout:
        try:
            blob = json.loads(r.stdout)
        except json.JSONDecodeError:
            blob = {"raw": r.stdout, "stderr": r.stderr}
    else:
        blob = {"error": r.stderr or r.stdout or f"exit {r.returncode}"}
    report_path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cands = blob.get("candidates") or []
    lines = [
        "# G2 OCR 候选频率（须人眼核对）",
        "",
        f"> generated: {datetime.now(timezone.utc).isoformat()}",
        f"> images: {', '.join(p.name for p in images)}",
        "",
        "## 候选",
        "",
    ]
    if not cands:
        lines.append("（无候选 — 请裁剪到频率读数区、提高对比度后重试）")
    else:
        lines.append("| # | Hz | raw | file |")
        lines.append("|---|-----|-----|------|")
        for i, c in enumerate(cands):
            lines.append(
                f"| {i} | {c.get('hz')} | `{c.get('raw')}` | {c.get('file', '')} |"
            )
    lines += [
        "",
        "## 确认后写入 inbox",
        "",
        "```bash",
        f"python3 scripts/ocr_scope_hz.py {' '.join(str(p) for p in images)} "
        "--as-c2 0 --as-c3-same --write-clocks --confirm-measured",
        "python3 scripts/ingest_g2_inbox.py",
        "python3 scripts/apply_g0_backfill.py --apply",
        "```",
        "",
        f"JSON: `{rel(report_path)}`",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {md_path}")
    print(f"WROTE {report_path}")
    print(
        "OCR-ONLY inbox: review candidates, then --write-clocks --confirm-measured "
        "(not yet usable for Must)",
        file=sys.stderr,
    )
    return 3


def run_ingest(inbox: Path, args, demo_banner: bool = False) -> int:
    inbox.mkdir(parents=True, exist_ok=True)
    out_dir = inbox / "_derived"
    out_dir.mkdir(parents=True, exist_ok=True)
    is_default = inbox == DEFAULT_INBOX.resolve()
    out_report = (
        ROOT / "05_tests" / "G2_inbox_infer_report.md"
        if is_default and not demo_banner
        else inbox / "G2_inbox_infer_report.md"
    )

    clocks = inbox / "g2_clocks.json"
    if not clocks.is_file():
        clocks = inbox / "clocks.json"
    csv_candidates = sorted(inbox.glob("*.csv")) + sorted(inbox.glob("spi*.csv"))
    # de-dup; never treat tracked examples/ as real G2 captures (unless demo_inbox)
    seen = set()
    csvs = []
    for c in csv_candidates:
        if c.resolve() in seen:
            continue
        if not demo_banner and (c.parent.name == "examples" or "example" in c.name.lower()):
            continue
        seen.add(c.resolve())
        csvs.append(c)

    clocks_usable = False
    clocks_filled: list[str] = []
    if clocks.is_file():
        data = json.loads(clocks.read_text(encoding="utf-8"))
        clocks_filled = [c["id"] for c in data if c.get("hz") is not None]
        clocks_usable = bool(clocks_filled)

    scope_imgs = []
    if not demo_banner:
        for pat in ("*.jpg", "*.jpeg", "*.png", "*.webp", "scope*"):
            for p in sorted(inbox.glob(pat)):
                if p.parent.name == "examples" or "example" in p.name.lower():
                    continue
                if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                    if p.resolve() not in {x.resolve() for x in scope_imgs}:
                        scope_imgs.append(p)

    if not clocks_usable and not csvs:
        if scope_imgs:
            return run_ocr_hint(inbox, scope_imgs, out_dir)
        print(
            f"EMPTY inbox: place g2_clocks.json (with measured hz) "
            f"and/or spi_capture.csv in {inbox}",
            file=sys.stderr,
        )
        if clocks.is_file() and not clocks_usable:
            print(
                "NOTE: g2_clocks.json present but all hz are null — not usable for P1.3",
                file=sys.stderr,
            )
        print(f"See template: {DEFAULT_INBOX / 'g2_clocks.template.json'}", file=sys.stderr)
        print(
            "Or drop a scope screenshot (*.jpg) and re-run — OCR will list Hz candidates.",
            file=sys.stderr,
        )
        print(f"Synthetic demos: python3 scripts/ingest_g2_inbox.py --demo", file=sys.stderr)
        return 2

    lines = [
        "# G2 inbox infer report",
        "",
        f"> generated: {datetime.now(timezone.utc).isoformat()}",
        f"> inbox: `{rel(inbox)}`",
    ]
    if demo_banner:
        lines += [
            "",
            "> **DEMO / SYNTHETIC** — Conserviss-min + plan-B clocks. **禁止**回填 G0 / Must。",
        ]
    lines += ["", "## Input hashes", ""]
    infer_cmd = [sys.executable, str(SCRIPTS / "g2_mode_infer.py")]
    spi_json = None

    if clocks.is_file():
        lines.append(f"- `{clocks.name}` sha256=`{sha256(clocks)}`")
        if not clocks_usable:
            lines.append("  - **WARN**: all hz are null — not usable for P1.3")
        else:
            infer_cmd += ["--clocks", str(clocks)]
            lines.append(f"  - filled points: {', '.join(clocks_filled)}")

    if csvs:
        csv_path = csvs[0]
        if len(csvs) > 1:
            lines.append(f"- NOTE: multiple CSV; using `{csv_path.name}`")
        lines.append(f"- `{csv_path.name}` sha256=`{sha256(csv_path)}`")
        spi_json = out_dir / "g2_spi_decode.json"
        cmd = [
            sys.executable,
            str(SCRIPTS / "decode_spi_capture.py"),
            str(csv_path),
            "--auto-map",
            "--json",
            str(spi_json),
        ]
        if getattr(args, "sclk", None):
            cmd += ["--sclk", args.sclk]
        if getattr(args, "mosi", None):
            cmd += ["--mosi", args.mosi]
        if getattr(args, "cs_adc", None):
            cmd += ["--cs-adc", args.cs_adc]
        if getattr(args, "cs_dac", None):
            cmd += ["--cs-dac", args.cs_dac]
        if getattr(args, "cs_cdce", None):
            cmd += ["--cs-cdce", args.cs_cdce]
        print("RUN", " ".join(cmd))
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            lines.append("- **ERROR**: decode_spi_capture failed")
            out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return r.returncode
        lines.append(f"- derived `{rel(spi_json)}` sha256=`{sha256(spi_json)}`")
        infer_cmd += ["--spi", str(spi_json)]

    lines += ["", "## g2_mode_infer", "", "```json"]
    infer_json_path = out_dir / "g2_mode_infer.json"
    hashes: dict[str, str] = {}
    if clocks.is_file() and clocks_usable:
        hashes[clocks.name] = sha256(clocks)
    if spi_json and spi_json.is_file():
        hashes[rel(spi_json)] = sha256(spi_json)

    out = ""
    infer_blob: dict = {}
    if len(infer_cmd) == 2:
        lines.append('{"skipped": true}')
    else:
        print("RUN", " ".join(infer_cmd))
        r = subprocess.run(infer_cmd, cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0:
            lines.append(out.rstrip() or "(no output)")
            lines.append(f"exit={r.returncode}")
        else:
            lines.append((r.stdout or "").rstrip() or "(no output)")
            try:
                infer_blob = json.loads(r.stdout or "{}")
            except json.JSONDecodeError:
                infer_blob = {}
            if infer_blob:
                if spi_json and spi_json.is_file():
                    try:
                        spi_blob = json.loads(spi_json.read_text(encoding="utf-8"))
                        if "checklist" in spi_blob:
                            infer_blob["checklist"] = spi_blob["checklist"]
                            # Attach CDCE Table-8 prior when Conserviss (or named) profile wins
                            best = spi_blob["checklist"].get("best_cdce_profile")
                            if best in ("conserviss", "e2e_internal", "e2e_external"):
                                profile_arg = (
                                    "conserviss"
                                    if best == "conserviss"
                                    else (
                                        "e2e_internal"
                                        if best == "e2e_internal"
                                        else "e2e_external"
                                    )
                                )
                                cp = subprocess.run(
                                    [
                                        sys.executable,
                                        str(SCRIPTS / "decode_cdce_profile.py"),
                                        "--profile",
                                        profile_arg,
                                    ],
                                    cwd=ROOT,
                                    capture_output=True,
                                    text=True,
                                )
                                if cp.returncode == 0 and cp.stdout:
                                    try:
                                        infer_blob["cdce_profile_prior"] = json.loads(cp.stdout)
                                    except json.JSONDecodeError:
                                        pass
                    except (json.JSONDecodeError, OSError):
                        pass
                infer_json_path.write_text(
                    json.dumps(infer_blob, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                hashes[rel(infer_json_path)] = sha256(infer_json_path)

    lines.append("```")
    if infer_blob.get("cdce_profile_prior"):
        lines += [
            "",
            "## CDCE profile prior (Table-8)",
            "",
            "```json",
            json.dumps(infer_blob["cdce_profile_prior"], ensure_ascii=False, indent=2),
            "```",
        ]

    proposal = (
        ROOT / "05_tests" / "G2_G0回填提案.md"
        if is_default and not demo_banner
        else inbox / "G2_G0回填提案.md"
    )
    if infer_blob:
        hash_path = out_dir / "input_hashes.json"
        hash_path.write_text(json.dumps(hashes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        prop_cmd = [
            sys.executable,
            str(SCRIPTS / "propose_g0_backfill.py"),
            "--infer",
            str(infer_json_path),
            "--hashes",
            str(hash_path),
            "--out",
            str(proposal),
        ]
        print("RUN", " ".join(prop_cmd))
        subprocess.run(prop_cmd, cwd=ROOT, check=False)
        lines += [
            "",
            "## G0 backfill proposal",
            "",
            f"- `{rel(proposal)}`（须人工复核后才改 G0）",
            f"- `{rel(infer_json_path)}` sha256=`{hashes.get(rel(infer_json_path), '')}`",
        ]
        if demo_banner:
            lines.append("- **DEMO：勿粘贴进 G0**")

    lines += [
        "",
        "## Next",
        "",
        "1. 复核 `G2_G0回填提案.md`（等级与哈希）",
        "2. `python3 scripts/apply_g0_backfill.py` 预览 → 确认后加 `--apply`"
        + (" --power-on-only" if False else "")
        + " 写回 G0 / `G2_时钟与SPI记录.md`",
        "3. `python3 scripts/audit_must.py --write-md`；P1.3/P1.4 达 ✅ 或强 🔶 → Must-1",
        "4. 再开 G3（勿跳）",
        "",
    ]
    out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {out_report}")
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
