#!/usr/bin/env python3
"""Cross-check packing + EP01 arm + FX2 stream-path toward acquisition restore.

Writes manifests/restore_crosscheck.json and refreshes RESTORE_PROGRESS.md body tables.
Confidence never exceeds candidate without stimulus/EEPROM.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manifests" / "restore_crosscheck.json"
PROGRESS = ROOT / "RESTORE_PROGRESS.md"


def load(name: str) -> dict:
    p = ROOT / "manifests" / name
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    pack = load("ep84_packing_deep.json")
    arm = load("ep01_stream_arm_sequence.json")
    stream = load("fx2_stream_path.json")
    oracle = load("fx2_oracle_crosscheck.json")
    preview = load("ep84_unpack_preview.json")

    layers = [
        {
            "layer": "USB_command_plane",
            "restored": "framing + opcode inventory + arm-window consensus sequence",
            "artifact": "ep01_stream_arm_sequence.json / usb_command_taxonomy.json",
            "confidence": "candidate",
            "missing": "opcode semantics, minimal recipe proof via replay",
        },
        {
            "layer": "USB_data_plane_bytes",
            "restored": "EP84 as primary sample bulk IN; length%4==0; headerless BE32>>7 top model",
            "artifact": "ep84_packing_deep.json / ep84_unpack_preview.json",
            "confidence": pack.get("top_hypothesis", {}).get("confidence") or "hypothesis",
            "missing": "volts scale, signedness, channel interleave proof",
        },
        {
            "layer": "FX2_firmware_path",
            "restored": "0x1435 hub FIFO/EP micro-ops; init→0x1435; opcode imm sites",
            "artifact": "fx2_stream_path.json / MCU_NOTES.md",
            "confidence": stream.get("confidence") or "candidate",
            "missing": "full CFG, indirect calls, eeprom.bin",
        },
        {
            "layer": "joint_oracle",
            "restored": "0x08 owner ∩ 0x1435 ∩ EP84-precede",
            "artifact": "fx2_oracle_crosscheck.json",
            "confidence": (oracle.get("headline") or {}).get("confidence") or "hypothesis",
            "missing": "proof 0x08 is start vs FIFO constant",
        },
        {
            "layer": "analog_frontend_FPGA",
            "restored": "architecture sketch only (BNC→relay→ADC→FPGA→FX2)",
            "artifact": "ARCHITECTURE.md / system_map.json",
            "confidence": "hypothesis",
            "missing": "bitstream behavior, coupling/IEPE/trigger experiments",
        },
        {
            "layer": "host_output_API",
            "restored": "API sketch mapped to EP01/81 + EP84",
            "artifact": "HOST_ACQ_API_SKETCH.md",
            "confidence": "hypothesis",
            "missing": "working open-source stack validated on live device",
        },
    ]

    blockers = pack.get("blocks_full_restore") or []
    blockers = list(dict.fromkeys(list(blockers) + [
        "No controlled stimulus capture in phase_b/captures/",
        "eeprom.bin still missing (L7)",
        "Cannot auto-upgrade to confirmed under catalog policy",
    ]))

    pct_parts = {
        "usb_transport_and_framing": 0.85,
        "stream_arm_sequence_structure": 0.55,
        "sample_word_structure": 0.60,
        "sample_physical_units": 0.05,
        "channel_map_and_sync": 0.10,
        "fx2_datapath_anchors": 0.50,
        "fpga_analog_behavior": 0.15,
        "host_end_to_end_restore": 0.20,
    }
    overall = sum(pct_parts.values()) / len(pct_parts)

    report = {
        "generated_at": now,
        "status": "partial_restore",
        "overall_restore_fraction_estimate": round(overall, 3),
        "fraction_note": "Heuristic coverage of reverse-engineering facets; NOT product equivalence",
        "facets": pct_parts,
        "layers": layers,
        "top_packing": pack.get("top_hypothesis"),
        "arm_first_occurrence_chain": arm.get("longest_common_first_occurrence_chain"),
        "oracle_headline": oracle.get("headline"),
        "unpack_preview_status": preview.get("status"),
        "blockers_to_full_restore": blockers,
        "next_actions": [
            "Lab: known sine/DC on AI0 alone → validate packing + scale",
            "Lab: 4ch common-source → channel interleave",
            "Replay white-list arm recipe from ep01_stream_arm_sequence.json",
            "Physical eeprom.bin dump for L7 firmware truth",
        ],
        "confidence_ceiling": "candidate",
        "declaration": "目录完整 ≠ 厂商等价 ≠ 掌握运行行为",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 采集链路还原进度",
        "",
        "> **声明：目录完整 ≠ 厂商等价 ≠ 掌握运行行为。**",
        f"> 自动刷新于 `{now}`。整体还原估计 **{overall:.0%}**（启发式，非厂商等价）。",
        "",
        "## 分层状态",
        "",
        "| 层 | 已还原 | 置信 | 仍缺 |",
        "|----|--------|------|------|",
    ]
    for L in layers:
        lines.append(
            f"| `{L['layer']}` | {L['restored']} | {L['confidence']} | {L['missing']} |"
        )
    lines += [
        "",
        "## 当前最强候选",
        "",
        f"- 打包：`{(pack.get('top_hypothesis') or {}).get('id')}` — {(pack.get('top_hypothesis') or {}).get('statement')}",
        f"- 启动链（首现）：`{' → '.join(arm.get('longest_common_first_occurrence_chain') or [])}`",
        f"- 固件枢纽：`0x1435`（FIFO/EP micro-ops + oracle 与 `0x08` 关联）",
        "",
        "## 完全还原阻塞",
        "",
    ]
    for b in blockers:
        lines.append(f"- {b}")
    lines += [
        "",
        "## 下一步",
        "",
    ]
    for a in report["next_actions"]:
        lines.append(f"1. {a}")
    lines += [
        "",
        "## 相关 manifests",
        "",
        "- `manifests/restore_crosscheck.json`",
        "- `manifests/ep84_packing_deep.json`",
        "- `manifests/ep01_stream_arm_sequence.json`",
        "- `manifests/fx2_stream_path.json`",
        "- `manifests/ep84_unpack_preview.json`",
        "",
    ]
    PROGRESS.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"overall": overall, "layers": len(layers), "blockers": len(blockers)}, indent=2))


if __name__ == "__main__":
    main()
