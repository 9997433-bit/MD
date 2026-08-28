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
    args = ap.parse_args()
    inbox: Path = args.inbox.resolve()
    inbox.mkdir(parents=True, exist_ok=True)
    out_dir = inbox / "_derived"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_report = (
        ROOT / "05_tests" / "G2_inbox_infer_report.md"
        if inbox == DEFAULT_INBOX.resolve()
        else inbox / "G2_inbox_infer_report.md"
    )

    clocks = inbox / "g2_clocks.json"
    if not clocks.is_file():
        clocks = inbox / "clocks.json"
    csv_candidates = sorted(inbox.glob("*.csv")) + sorted(inbox.glob("spi*.csv"))
    # de-dup; never treat tracked examples/ as real G2 captures
    seen = set()
    csvs = []
    for c in csv_candidates:
        if c.resolve() in seen:
            continue
        if c.parent.name == "examples" or "example" in c.name.lower():
            continue
        seen.add(c.resolve())
        csvs.append(c)

    clocks_usable = False
    clocks_filled: list[str] = []
    if clocks.is_file():
        data = json.loads(clocks.read_text(encoding="utf-8"))
        clocks_filled = [c["id"] for c in data if c.get("hz") is not None]
        clocks_usable = bool(clocks_filled)

    if not clocks_usable and not csvs:
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
        print(f"See template: {inbox / 'g2_clocks.template.json'}", file=sys.stderr)
        print(f"Synthetic column demos: {inbox / 'examples'}/ (not auto-ingested)", file=sys.stderr)
        return 2

    lines = [
        "# G2 inbox infer report",
        "",
        f"> generated: {datetime.now(timezone.utc).isoformat()}",
        f"> inbox: `{rel(inbox)}`",
        "",
        "## Input hashes",
        "",
    ]
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
        if args.sclk:
            cmd += ["--sclk", args.sclk]
        if args.mosi:
            cmd += ["--mosi", args.mosi]
        if args.cs_adc:
            cmd += ["--cs-adc", args.cs_adc]
        if args.cs_dac:
            cmd += ["--cs-dac", args.cs_dac]
        if args.cs_cdce:
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
                    except (json.JSONDecodeError, OSError):
                        pass
                infer_json_path.write_text(
                    json.dumps(infer_blob, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                hashes[rel(infer_json_path)] = sha256(infer_json_path)

    lines.append("```")

    proposal = (
        ROOT / "05_tests" / "G2_G0回填提案.md"
        if inbox == DEFAULT_INBOX.resolve()
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

    lines += [
        "",
        "## Next (human)",
        "",
        "1. 复核 `G2_G0回填提案.md` → 写入 `G2_时钟与SPI记录.md` 与 `G0_命题基线证据表.md`",
        "2. 改等级时附上本报告中的 sha256",
        "3. 未达标勿开 G3 算法定性",
        "",
    ]
    out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {out_report}")
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
