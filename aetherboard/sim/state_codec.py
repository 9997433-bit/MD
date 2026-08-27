"""Export Python battle state to schema-aligned JSON."""

from __future__ import annotations

import json
from typing import Any

from .types import BattleState, CellKind, Job, Phase, Telegraph


def _phase_name(phase: Phase) -> str:
    return phase.name


def _telegraph_name(t: Telegraph) -> str:
    return t.name


def _job_name(job: Job) -> str:
    return job.value


def _cell_name(c: CellKind) -> str:
    return c.name


def state_to_dict(state: BattleState, boss_id: str, preview_cells: list | None = None) -> dict[str, Any]:
    preview = preview_cells or []
    return {
        "turn": state.turn,
        "phase": _phase_name(state.phase),
        "boardSize": state.board_size,
        "bossId": boss_id,
        "boss": {
            "name": state.boss.name,
            "hp": state.boss.hp,
            "maxHp": state.boss.max_hp,
            "phase": state.boss.phase,
            "telegraph": _telegraph_name(state.boss.telegraph),
            "furyCastTurns": state.boss.fury_cast_turns,
            "shrinkLevel": state.boss.shrink_level,
            "alive": state.boss.alive,
        },
        "party": [
            {
                "id": u.id,
                "name": u.name,
                "job": _job_name(u.job),
                "pos": {"x": u.pos.x, "y": u.pos.y},
                "hp": u.hp,
                "maxHp": u.max_hp,
                "alive": u.alive,
                "moved": u.moved_this_turn,
                "gcdUsed": u.gcd_used,
                "ogcdUsed": u.ogcd_used,
                "mitTurns": u.mit_turns,
                "songTurns": u.bard_song_turns,
                "tauntTurns": u.taunt_turns,
            }
            for u in state.party
        ],
        "cells": [[_cell_name(state.cells[y][x]) for x in range(state.board_size)] for y in range(state.board_size)],
        "pendingHazards": [{"x": p.x, "y": p.y} for p in state.pending_hazards],
        "previewCells": [{"x": p.x, "y": p.y} for p in preview],
        "log": list(state.log.entries),
    }


def state_to_json(state: BattleState, boss_id: str) -> str:
    return json.dumps(state_to_dict(state, boss_id), ensure_ascii=False)
