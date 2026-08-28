#!/usr/bin/env python3
"""
从 g2_mode_infer JSON + 输入哈希生成《G2_G0回填提案.md》。

人工复核后才改 G0；本脚本只出可粘贴草案，缩短 Must 解锁回合。
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "05_tests" / "G2_G0回填提案.md"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--infer", type=Path, required=True, help="g2_mode_infer JSON")
    ap.add_argument("--hashes", type=Path, help="optional JSON {file: sha256}")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--power-on-only", action="store_true", help="SPI captured with host disconnected")
    args = ap.parse_args()

    infer = json.loads(args.infer.read_text(encoding="utf-8"))
    hashes = {}
    if args.hashes and args.hashes.is_file():
        hashes = json.loads(args.hashes.read_text(encoding="utf-8"))

    clocks = infer.get("clocks") or {}
    spi = infer.get("spi") or {}
    # optional nested checklist from decode JSON path via ingest-derived infer
    checklist = {}
    if isinstance(spi.get("notes"), list):
        pass
    # allow passing full decode blob as --infer with checklist key
    checklist = infer.get("checklist") or spi.get("checklist") or {}

    p13 = clocks.get("P1.3_suggested", "❓")
    p14 = spi.get("P1.4_suggested", "❓")
    p15 = spi.get("P1.5_suggested", "❓")
    if args.power_on_only and "位流内" in str(p15):
        p15 = "✅（仅上电无主机仍有 SPI → 位流内主控）"

    profile = checklist.get("best_cdce_profile", "—")
    ratio = checklist.get("conserviss_cdce_match_ratio", "—")
    dac_cfg = checklist.get("dac_cfg1_value", "—")
    dac_pre = checklist.get("conserviss_dac_pre_sync_ratio", "—")
    cdce_prior = infer.get("cdce_profile_prior") or {}

    lines = [
        "# G2 → G0 回填提案（自动生成 · 须人工复核）",
        "",
        f"> generated: {datetime.now(timezone.utc).isoformat()}",
        "> **禁止**未复核直接改 G0；Must 以人工粘贴后的 `G0_命题基线证据表.md` 为准。",
        "",
        "## 建议等级",
        "",
        "| 命题 | 建议 | 依据摘要 |",
        "|------|------|----------|",
        f"| P1.3 | {p13} | {'; '.join(clocks.get('notes') or []) or '（无钟）'} |",
        f"| P1.4 | {p14} | {'; '.join(spi.get('notes') or []) or '（无 SPI）'} |",
        f"| P1.5 | {p15} | 仅上电实验标记={args.power_on_only} |",
        f"| H8 | {clocks.get('H8', '—')} | interp_hint={clocks.get('interp_hint')} |",
        f"| CDCE 剖面 | {profile} | Conserviss match_ratio={ratio}; DAC CONFIG1={dac_cfg}; pre_sync_ratio={dac_pre} |",
        "",
    ]
    if cdce_prior:
        lines += [
            "## CDCE 分频先验（decode_cdce_profile · 非实测）",
            "",
            f"- profile=`{cdce_prior.get('profile')}` plan_hint=`{cdce_prior.get('plan_hint')}`",
            f"- G2 先验: `{json.dumps(cdce_prior.get('g2_prior') or {}, ensure_ascii=False)}`",
            "- **仅当**实测 SPI 剖面匹配且布线同构时，用此先验对表 C2/C3；**不得**单独升 P1.3",
            "",
        ]
    lines += [
        "## Must-1 缺口速查",
        "",
        f"- P1.3 仍需实测钟：{'已有建议 ' + str(p13) if p13 not in ('❓', None) else '**缺** g2_clocks.json'}",
        f"- P1.4 仍需 SPI：{'已有建议 ' + str(p14) if p14 not in ('❓', None) else '**缺** spi_capture.csv'}",
        "- P1.1/P1.2：静态 🔶；边沿/蜂鸣另计",
        "",
        "## 输入哈希",
        "",
    ]
    if hashes:
        for k, v in hashes.items():
            lines.append(f"- `{k}` sha256=`{v}`")
    else:
        lines.append("- （未提供 — 从 `G2_inbox_infer_report.md` 抄）")

    lines += [
        "",
        "## 粘贴到 G0 的草稿句式",
        "",
        "```text",
        f"P1.3：{p13} — 见 G2 记录 + inbox infer；哈希见上。",
        f"P1.4：{p14} — SPI checklist / decode JSON；哈希见上。",
        f"P1.5：{p15}",
        "```",
        "",
        "## 下一步",
        "",
        "1. 人工打开 `G2_时钟与SPI记录.md` 填表并勾选靶标",
        "2. 改 `G0_命题基线证据表.md` 对应节等级 + 附哈希",
        "3. 重跑 `Must完成审计_当前缺口.md`；若 P1.3/P1.4 达 ✅ 或强 🔶 → Must-1 翻转",
        "4. 再开 G3（勿跳）",
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
