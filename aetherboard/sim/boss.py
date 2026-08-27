"""Earth Guardian boss inspired by classic trial pacing."""

from __future__ import annotations

import random
from typing import Optional

from .board import apply_hazards, apply_shrink, clear_hazards, positions_in_radius
from .types import BossState, Pos, Telegraph


def create_boss() -> BossState:
    return BossState(name="土灵守护者", hp=6000, max_hp=6000)


def update_boss_phase(boss: BossState) -> None:
    ratio = boss.hp_ratio
    if ratio <= 0.4:
        boss.phase = 3
    elif ratio <= 0.7:
        boss.phase = 2
    else:
        boss.phase = 1


def telegraph_for_phase(boss: BossState, rng: random.Random) -> Telegraph:
    if boss.phase == 1:
        return Telegraph.SLAM
    if boss.phase == 2:
        return Telegraph.EARTHQUAKE
    if boss.fury_cast_turns > 0:
        return Telegraph.EARTHEN_FURY
    if boss.shrink_level < 1:
        return Telegraph.SHRINK
    return Telegraph.EARTHEN_FURY


def warning_message(telegraph: Telegraph) -> str:
    messages = {
        Telegraph.SLAM: "Boss 预备重击：中心 1 格范围将受重创。",
        Telegraph.EARTHQUAKE: "Boss 预备地震：随机区域将出现危险格。",
        Telegraph.SHRINK: "Boss 预备缩圈：外圈将变为即死区。",
        Telegraph.EARTHEN_FURY: "Boss 开始读条「土神之怒」：2 回合内必须打断！",
        Telegraph.NONE: "",
    }
    return messages[telegraph]


def slam_targets(size: int) -> list[Pos]:
    center = Pos(size // 2, size // 2)
    return positions_in_radius(center, 1, size)


def earthquake_hazards(size: int, rng: random.Random) -> list[Pos]:
    center = Pos(rng.randint(1, size - 2), rng.randint(1, size - 2))
    return positions_in_radius(center, 1, size)


def boss_slam_damage() -> int:
    return 220


def boss_quake_damage() -> int:
    return 160


def boss_fury_damage() -> int:
    return 9999


def boss_basic_damage(boss: BossState) -> int:
    if boss.phase == 1:
        return 140
    if boss.phase == 2:
        return 180
    return 220
