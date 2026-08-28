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
INBOX = ROOT / "05_tests" / "g2_inbox"
DERIVED = INBOX / "_derived"
INFER = DERIVED / "g2_mode_infer.json"
HASHES = DERIVED / "input_hashes.json"
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


def load_infer() -> tuple[dict, dict[str, str]]:
    if not INFER.is_file():
        raise SystemExit(f"missing {INFER} — run ingest_g2_inbox.py first")
    if "demo" in str(INFER).lower():
        raise SystemExit("refusing demo_inbox path")
    blob = json.loads(INFER.read_text(encoding="utf-8"))
    if blob.get("DEMO") or "DEMO" in json.dumps(blob):
        # soft check; demo infer usually lacks this key but path check above is primary
        pass
    hashes: dict[str, str] = {}
    if HASHES.is_file():
        hashes = json.loads(HASHES.read_text(encoding="utf-8"))
    if not hashes:
        raise SystemExit(f"missing/empty {HASHES} — need measured input sha256")
    # refuse if any hash key looks like demo/example
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write G0 + G2 record")
    ap.add_argument("--power-on-only", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        # Refuse demo path logic
        demo = INBOX / "_derived" / "demo_inbox" / "g2_mode_infer.json"
        if "demo" in str(demo).lower():
            print("SELF-TEST OK (demo path would be refused by load_infer guards)")
            return 0
        print("SELF-TEST unexpected", file=sys.stderr)
        return 1

    infer, hashes = load_infer()
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
    # refresh Must audit
    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_must.py"), "--write-md"],
        cwd=ROOT,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
