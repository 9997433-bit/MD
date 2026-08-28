#!/usr/bin/env python3
"""
机器核验 Must（研究计划 §5）— 禁止在未达标时标 goal complete。

检查：
  Must-1: G0 中 P1.1–P1.4 均为 ✅ 或「强 🔶」
  Must-2: G3G4 §4.2 算法模块排除表非空（无「（空）」行）
  Must-3: g2_inbox 根目录有可用实测钟或 SPI，且存在带 sha256 的 G2 记录/提案

用法：
  python3 scripts/audit_must.py
  python3 scripts/audit_must.py --write-md   # 刷新 06_docs/Must完成审计_当前缺口.md
退出码：0=Must 全过；1=未过；2=环境/文件异常
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
MATRIX = ROOT / "05_tests" / "G3G4_算法判别矩阵.md"
INBOX = ROOT / "05_tests" / "g2_inbox"
MUST_MD = ROOT / "06_docs" / "Must完成审计_当前缺口.md"
ACCEPT = {"✅", "强🔶", "强 🔶"}


def parse_g0_grades(text: str) -> dict[str, str]:
    """Extract '### P1.x … —— 当前 **GRADE**' headings."""
    grades: dict[str, str] = {}
    for m in re.finditer(
        r"###\s+(P1\.\d)\s+[^\n—]*——\s*当前\s+\*\*([^*]+)\*\*",
        text,
    ):
        grades[m.group(1)] = m.group(2).strip()
    return grades


def section_42_empty(text: str) -> bool:
    # After ### 4.2 ... look for a table row that is only （空）
    idx = text.find("### 4.2")
    if idx < 0:
        return True
    chunk = text[idx : idx + 800]
    return "（空）" in chunk or "| （空） |" in chunk or "|（空）|" in chunk


def inbox_measured() -> dict:
    clocks = INBOX / "g2_clocks.json"
    if not clocks.is_file():
        clocks = INBOX / "clocks.json"
    csvs = [
        p
        for p in list(INBOX.glob("*.csv")) + list(INBOX.glob("spi*.csv"))
        if p.parent.name != "examples" and "example" not in p.name.lower()
    ]
    filled: list[str] = []
    if clocks.is_file():
        try:
            data = json.loads(clocks.read_text(encoding="utf-8"))
            filled = [c["id"] for c in data if c.get("hz") is not None]
        except (json.JSONDecodeError, TypeError, KeyError):
            filled = []
    return {
        "clocks_file": clocks.is_file(),
        "clocks_filled": filled,
        "spi_csvs": [p.name for p in csvs],
        "usable": bool(filled) or bool(csvs),
    }


def audit() -> dict:
    g0_text = G0.read_text(encoding="utf-8") if G0.is_file() else ""
    matrix_text = MATRIX.read_text(encoding="utf-8") if MATRIX.is_file() else ""
    grades = parse_g0_grades(g0_text)
    p11_p14 = {k: grades.get(k, "❓") for k in ("P1.1", "P1.2", "P1.3", "P1.4")}
    must1_ok = all(
        g.replace(" ", "") in {a.replace(" ", "") for a in ACCEPT} or g == "✅"
        for g in p11_p14.values()
    )
    # normalize: accept ✅ or 强🔶 (with optional space)
    def ok_grade(g: str) -> bool:
        s = g.replace(" ", "")
        return s == "✅" or s == "强🔶"

    must1_ok = all(ok_grade(g) for g in p11_p14.values())
    must2_mod_empty = section_42_empty(matrix_text)
    must2_ok = not must2_mod_empty  # strict: module exclusion table must have rows
    inbox = inbox_measured()
    # Must-3: measured data present AND a G2 record or proposal with sha256
    records = list((ROOT / "05_tests").glob("G2*.md")) + list(
        (ROOT / "05_tests").glob("*回填*.md")
    )
    hash_docs = []
    for p in records:
        t = p.read_text(encoding="utf-8", errors="ignore")
        if "sha256" in t.lower() and inbox["usable"]:
            # exclude demo paths mentioned as DEMO
            if "DEMO" in t and "禁止" in t:
                continue
            hash_docs.append(p.name)
    # Also accept inbox-derived proposal only if not under demo_inbox and inbox usable
    proposal = ROOT / "05_tests" / "G2_G0回填提案.md"
    if proposal.is_file() and inbox["usable"]:
        pt = proposal.read_text(encoding="utf-8", errors="ignore")
        if "sha256" in pt.lower() and "DEMO" not in pt:
            hash_docs.append(proposal.name)
    must3_ok = inbox["usable"] and bool(hash_docs)

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "grades": p11_p14,
        "must1": {"ok": must1_ok, "grades": p11_p14},
        "must2": {"ok": must2_ok, "section_42_empty": must2_mod_empty},
        "must3": {"ok": must3_ok, "inbox": inbox, "hash_docs": hash_docs},
        "must_all": must1_ok and must2_ok and must3_ok,
    }


def write_md(result: dict) -> None:
    g = result["grades"]
    inbox = result["must3"]["inbox"]
    lines = [
        "# Must 完成审计（当前 · " + ("达成" if result["must_all"] else "未达成") + "）",
        "",
        "> 对照 `算法与ADCDAC实现_研究计划.md` §5 **最低合格（Must）**。",
        f"> 由 `scripts/audit_must.py` 生成：{result['generated']}",
        "> 结论：**"
        + ("Must 达成。" if result["must_all"] else "Must 未达成 → 总目标未完成。禁止标 complete。")
        + "**",
        "",
        "---",
        "",
        "## 机器核验快照",
        "",
        "```text",
        f"g2_inbox usable: {inbox['usable']}; clocks_filled={inbox['clocks_filled']}; spi={inbox['spi_csvs']}",
        f"G0: P1.1={g['P1.1']} P1.2={g['P1.2']} P1.3={g['P1.3']} P1.4={g['P1.4']}",
        f"§4.2 empty: {result['must2']['section_42_empty']}",
        f"Must-1={result['must1']['ok']} Must-2={result['must2']['ok']} Must-3={result['must3']['ok']}",
        "```",
        "",
        "## Must-1",
        "",
        "| 命题 | 等级 | 达子条 |",
        "|------|------|--------|",
    ]
    for k, v in g.items():
        s = v.replace(" ", "")
        ok = s == "✅" or s == "强🔶"
        lines.append(f"| {k} | {v} | {'是' if ok else '**否**'} |")
    lines += [
        "",
        f"**Must-1：{'通过' if result['must1']['ok'] else '失败'}。**",
        "",
        "## Must-2",
        "",
        f"§4.2 算法模块排除表空：{result['must2']['section_42_empty']}",
        f"**Must-2：{'通过' if result['must2']['ok'] else '失败/部分'}。**",
        "",
        "## Must-3",
        "",
        f"实测 inbox：{inbox}",
        f"含 sha256 的 G2 文档：{result['must3']['hash_docs'] or '（无）'}",
        f"**Must-3：{'通过' if result['must3']['ok'] else '失败'}。**",
        "",
        "## 解锁",
        "",
        "`G2_投放三步.md` → 根目录实测 → `ingest_g2_inbox.py` → "
        "`apply_g0_backfill.py --apply` → 再跑本脚本（`--write-md`）。",
        "",
    ]
    MUST_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {MUST_MD}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-md", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not G0.is_file():
        print(f"missing {G0}", file=sys.stderr)
        return 2
    result = audit()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"Must-1={result['must1']['ok']} grades={result['grades']}\n"
            f"Must-2={result['must2']['ok']} §4.2_empty={result['must2']['section_42_empty']}\n"
            f"Must-3={result['must3']['ok']} inbox={result['must3']['inbox']}\n"
            f"MUST_ALL={result['must_all']}"
        )
    if args.write_md:
        write_md(result)
    return 0 if result["must_all"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
