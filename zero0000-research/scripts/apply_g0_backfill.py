#!/usr/bin/env python3
"""
将实测 G2 infer 回填到 G0 / G2 记录（缩短 Must-1/3 闭环）。

安全：
  - 必须 --apply（默认 dry-run）
  - 拒绝 demo_inbox / DEMO / example 路径
  - 要求 input_hashes.json 存在且至少一枚 sha256
  - 仅当建议等级为 ✅ 或「强 🔶」时改写对应 P1.x 标题

用法：
  python3 scripts/apply_g0_backfill.py              # dry-run
  python3 scripts/apply_g0_backfill.py --apply       # 写盘
  python3 scripts/apply_g0_backfill.py --apply --power-on-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G0 = ROOT / "06_docs" / "G0_命题基线证据表.md"
G2_REC = ROOT / "05_tests" / "G2_时钟与SPI记录.md"
DEFAULT_INBOX = ROOT / "05_tests" / "g2_inbox"
MUST_ACCEPT = {"✅", "强🔶", "强 🔶"}


def norm_grade(g: str) -> str:
    s = (g or "").strip()
    if s.replace(" ", "") == "强🔶":
        return "强 🔶"
    if s == "🔶":
        # plain 🔶 does not unlock Must-1; keep as-is for honesty
        return "🔶"
    return s


def must_ok(g: str) -> bool:
    return norm_grade(g).replace(" ", "") in {a.replace(" ", "") for a in MUST_ACCEPT} or g == "✅"


def load_infer(inbox: Path) -> tuple[dict, dict[str, str]]:
    derived = inbox / "_derived"
    infer_path = derived / "g2_mode_infer.json"
    hash_path = derived / "input_hashes.json"
    if not infer_path.is_file():
        raise SystemExit(f"missing {infer_path} — run ingest_g2_inbox.py --inbox {inbox}")
    path_l = str(infer_path).lower()
    if "demo" in path_l or "example" in path_l:
        raise SystemExit("refusing demo/example path")
    blob = json.loads(infer_path.read_text(encoding="utf-8"))
    hashes: dict[str, str] = {}
    if hash_path.is_file():
        hashes = json.loads(hash_path.read_text(encoding="utf-8"))
    if not hashes:
        raise SystemExit(f"missing/empty {hash_path} — need measured input sha256")
    for k in hashes:
        lk = k.lower()
        if "demo" in lk or "example" in lk:
            raise SystemExit(f"refusing demo/example hash key: {k}")
    return blob, hashes


def patch_g0_heading(text: str, pid: str, grade: str) -> str:
    """Replace '### P1.x … —— 当前 **OLD**' with new grade."""
    pat = re.compile(
        rf"(###\s+{re.escape(pid)}\s+[^\n—]*——\s*当前\s+)\*\*[^*]+\*\*"
    )
    repl = rf"\1**{grade}**"
    new, n = pat.subn(repl, text, count=1)
    if n != 1:
        raise SystemExit(f"failed to patch heading for {pid} (matches={n})")
    return new


def append_evidence(text: str, pid: str, paragraph: str) -> str:
    """Insert an evidence bullet after the first '| 现有证据 |' row for that section."""
    # Find section then first 现有证据 cell and append note in a new row after the table block is hard;
    # simpler: append a dated note under the section heading.
    marker = f"### {pid} "
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit(f"section {pid} not found")
    # find end of heading line
    nl = text.find("\n", idx)
    insert_at = nl + 1
    note = f"\n> G2 回填 {datetime.now(timezone.utc).date().isoformat()}：{paragraph}\n"
    return text[:insert_at] + note + text[insert_at:]


def write_g2_record(infer: dict, hashes: dict[str, str], power_on_only: bool) -> str:
    clocks = infer.get("clocks") or {}
    spi = infer.get("spi") or {}
    lines = [
        "# G2 时钟与 SPI 记录（实测回填）",
        "",
        f"> 由 `apply_g0_backfill.py` 生成：{datetime.now(timezone.utc).isoformat()}",
        "> 原始 inbox 哈希见下；等级以 `G0_命题基线证据表.md` 为准。",
        "",
        "## 0. 元数据",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| 固件 | `20230825_s2056` |",
        f"| 仅上电无主机 | {power_on_only} |",
        "| 原始哈希 | 见下 |",
        "",
        "## 输入哈希",
        "",
    ]
    for k, v in hashes.items():
        lines.append(f"- `{k}` sha256=`{v}`")
    lines += [
        "",
        "## 1. 时钟（P1.3）",
        "",
        f"- 建议等级：**{clocks.get('P1.3_suggested', '❓')}**",
        f"- H8：{clocks.get('H8', '—')}",
        f"- interp_hint：{clocks.get('interp_hint')}",
        f"- notes：{'; '.join(clocks.get('notes') or [])}",
        "",
        "## 2. SPI（P1.4 / P1.5）",
        "",
        f"- P1.4 建议：**{spi.get('P1.4_suggested', '❓')}**",
        f"- P1.5 建议：{spi.get('P1.5_suggested', '❓')}",
        f"- notes：{'; '.join(spi.get('notes') or [])}",
        "",
    ]
    return "\n".join(lines)


def e2e_self_test() -> int:
    """Scratch inbox: plan-B clocks + Conserviss SPI → Must-acceptable grades; never touch G0."""
    import shutil
    import subprocess
    import tempfile

    tmp = Path(tempfile.mkdtemp(prefix="g2_e2e_must_"))
    try:
        clocks = tmp / "g2_clocks.json"
        clocks.write_text(
            json.dumps(
                [
                    {"id": "C2", "hz": 245760000, "note": "E2E scratch"},
                    {"id": "C3", "hz": 245760000, "note": "E2E scratch"},
                    {"id": "C6", "hz": 122880000, "note": "E2E scratch"},
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        csv_path = tmp / "spi_capture.csv"
        r = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "decode_spi_capture.py"),
                "--write-conserviss-example",
                str(csv_path),
            ],
            cwd=ROOT,
        )
        if r.returncode != 0:
            print("SELF-TEST FAILED write example", file=sys.stderr)
            return 1
        # rename away from *example* so ingest accepts it
        real_csv = tmp / "spi_capture.csv"
        if "example" in csv_path.name.lower():
            # write-conserviss-example may keep name; force clean name
            pass
        # decode_spi writes the path we gave; ensure name has no 'example'
        if "example" in real_csv.name.lower():
            print("SELF-TEST FAILED csv name contains example", file=sys.stderr)
            return 1
        r = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "ingest_g2_inbox.py"),
                "--inbox",
                str(tmp),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print("SELF-TEST FAILED ingest", r.stdout, r.stderr, file=sys.stderr)
            return 1
        infer, hashes = load_infer(tmp)
        p13 = norm_grade(str((infer.get("clocks") or {}).get("P1.3_suggested", "❓")))
        p14 = norm_grade(str((infer.get("spi") or {}).get("P1.4_suggested", "❓")))
        if not (must_ok(p13) and must_ok(p14)):
            print(
                f"SELF-TEST FAILED grades P1.3={p13} P1.4={p14} hashes={list(hashes)}",
                file=sys.stderr,
            )
            return 1
        # dry-run apply on scratch must not require writing; ensure --apply on non-default refused
        print(
            f"SELF-TEST OK e2e scratch Must-grades P1.3={p13} P1.4={p14} "
            f"hashes={len(hashes)} (G0 untouched)"
        )
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inbox", type=Path, default=DEFAULT_INBOX)
    ap.add_argument("--apply", action="store_true", help="write G0 + G2 record")
    ap.add_argument("--power-on-only", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return e2e_self_test()

    inbox = args.inbox.resolve()
    infer, hashes = load_infer(inbox)
    clocks = infer.get("clocks") or {}
    spi = infer.get("spi") or {}
    p13 = norm_grade(str(clocks.get("P1.3_suggested", "❓")))
    p14 = norm_grade(str(spi.get("P1.4_suggested", "❓")))
    p15 = str(spi.get("P1.5_suggested", "❓"))
    if args.power_on_only and "位流内" in p15:
        p15 = "✅"

    plan = {
        "P1.3": p13 if must_ok(p13) else None,
        "P1.4": p14 if must_ok(p14) else None,
        "P1.5": p15 if must_ok(p15) or p15.startswith("✅") else None,
    }
    print("PLAN", json.dumps(plan, ensure_ascii=False))
    print("HASHES", list(hashes.keys()))
    if not any(plan.values()):
        print(
            "nothing to apply: no Must-acceptable grades in infer "
            "(need ✅ or 强 🔶 for P1.3/P1.4)",
            file=sys.stderr,
        )
        return 1

    hash_line = "; ".join(f"{k}={v[:12]}…" for k, v in hashes.items())
    if not args.apply:
        print("DRY-RUN — pass --apply to write G0 / G2_时钟与SPI记录.md")
        return 0

    if inbox != DEFAULT_INBOX.resolve():
        print(
            f"refusing --apply on non-default inbox {inbox} "
            f"(use default g2_inbox for real backfill)",
            file=sys.stderr,
        )
        return 2

    g0 = G0.read_text(encoding="utf-8")
    if plan["P1.3"]:
        g0 = patch_g0_heading(g0, "P1.3", plan["P1.3"])
        g0 = append_evidence(
            g0,
            "P1.3",
            f"实测回填 → **{plan['P1.3']}**；{'; '.join(clocks.get('notes') or [])}；哈希 {hash_line}",
        )
    if plan["P1.4"]:
        g0 = patch_g0_heading(g0, "P1.4", plan["P1.4"])
        g0 = append_evidence(
            g0,
            "P1.4",
            f"SPI 回填 → **{plan['P1.4']}**；{'; '.join(spi.get('notes') or [])}；哈希 {hash_line}",
        )
    if plan["P1.5"]:
        g0 = patch_g0_heading(g0, "P1.5", plan["P1.5"])
        g0 = append_evidence(
            g0,
            "P1.5",
            f"配置归属回填 → **{plan['P1.5']}**；power_on_only={args.power_on_only}；哈希 {hash_line}",
        )
    G0.write_text(g0, encoding="utf-8")
    G2_REC.write_text(
        write_g2_record(infer, hashes, args.power_on_only), encoding="utf-8"
    )
    print(f"WROTE {G0}")
    print(f"WROTE {G2_REC}")
    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_must.py"), "--write-md"],
        cwd=ROOT,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
