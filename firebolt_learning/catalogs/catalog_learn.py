"""LEARN-* : 学习检查清单（阶段 F 自测）。"""
from __future__ import annotations

from typing import Any

LEARN_ENTRIES: list[tuple[str, str, str, str, str]] = [
    (
        "LEARN-Q1-SYNC-LAYER",
        "Can explain sync layer (ADC shared convert vs software align)",
        "confirmed",
        "checklist",
        "Answer keyed to SPEC-SYNC-LAYER + HW-SYNC-LOCUS",
    ),
    (
        "LEARN-Q2-16-VS-32",
        "Can explain 16-ch simultaneous vs 32-SE bank",
        "confirmed",
        "checklist",
        "SPEC-SIM-* / SPEC-SE-PAIR / SPEC-BANK",
    ),
    (
        "LEARN-Q3-CLOCK-TRIG-AICONV",
        "Can separate sample clock, start trigger, AIConv roles",
        "confirmed",
        "checklist",
        "SPEC timing + PFI + AIConv",
    ),
    (
        "LEARN-Q4-FX3-VS-FPGA",
        "Can state FX3 vs FPGA responsibilities",
        "confirmed",
        "checklist",
        "FX3-ROLE-SUMMARY vs BIT unknowns",
    ),
    (
        "LEARN-Q5-FRAME-PACK",
        "Can state FIFO->USB packing only as unknown/hypothesis",
        "confirmed",
        "checklist",
        "Must not over-claim; see forced null bridges",
    ),
    (
        "LEARN-Q6-UPGRADE-PATH",
        "Can list capture/netlist/lab upgrades for unknowns",
        "confirmed",
        "checklist",
        "OMISSIONS_AND_REMAINING.md",
    ),
    (
        "LEARN-NO-VENDOR-EQ",
        "Accept stop condition: complete catalog != vendor equivalence",
        "confirmed",
        "policy",
        "README declaration",
    ),
    (
        "LEARN-NO-CAPTURE-YET",
        "Acknowledge USB capture deferred this phase",
        "confirmed",
        "policy",
        "PHASE_PLAN deferred list",
    ),
]


def build_entries() -> list[dict[str, Any]]:
    return [
        {
            "identifier": i,
            "module": "learn",
            "source_identifier": t,
            "status": s,
            "boundary": b,
            "note": n,
        }
        for i, t, s, b, n in LEARN_ENTRIES
    ]


def entry_ids() -> list[str]:
    return [e[0] for e in LEARN_ENTRIES]
