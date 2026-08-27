"""Boss profile protocol and registry."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from ..board import positions_in_radius
from ..types import BossState, Pos, Telegraph


@dataclass
class TelegraphPreview:
    telegraph: Telegraph
    message: str
    danger_cells: list[Pos]


class BossProfile(Protocol):
    boss_id: str

    def create(self) -> BossState: ...

    def update_phase(self, boss: BossState) -> None: ...

    def pick_telegraph(self, boss: BossState, rng: random.Random) -> Telegraph: ...

    def preview(self, telegraph: Telegraph, board_size: int, boss: BossState) -> TelegraphPreview: ...

    def resolve_mechanic(
        self,
        telegraph: Telegraph,
        boss: BossState,
        board_size: int,
        rng: random.Random,
    ) -> tuple[list[Pos], list[str]]: ...

    def basic_damage(self, boss: BossState) -> int: ...

    def fury_name(self) -> str: ...

    def victory_message(self) -> str: ...


def _center(size: int) -> Pos:
    return Pos(size // 2, size // 2)


class EarthGuardianBoss:
    boss_id = "earth"

    def create(self) -> BossState:
        return BossState(name="土灵守护者", hp=4200, max_hp=4200, boss_id=self.boss_id)

    def update_phase(self, boss: BossState) -> None:
        ratio = boss.hp_ratio
        if ratio <= 0.4:
            boss.phase = 3
        elif ratio <= 0.7:
            boss.phase = 2
        else:
            boss.phase = 1

    def pick_telegraph(self, boss: BossState, rng: random.Random) -> Telegraph:
        if boss.phase == 1:
            return Telegraph.SLAM
        if boss.phase == 2:
            return Telegraph.EARTHQUAKE
        if boss.fury_cast_turns > 0:
            return Telegraph.EARTHEN_FURY
        if boss.shrink_level < 1:
            return Telegraph.SHRINK
        return Telegraph.EARTHEN_FURY

    def preview(self, telegraph: Telegraph, board_size: int, boss: BossState) -> TelegraphPreview:
        messages = {
            Telegraph.SLAM: "Boss 预备重击：中心 3×3 将受重创。",
            Telegraph.EARTHQUAKE: "Boss 预备地震：随机 3×3 危险区。",
            Telegraph.SHRINK: "Boss 预备缩圈：外圈变为即死区。",
            Telegraph.EARTHEN_FURY: "Boss 读条「土神之怒」：2 回合内必须打断！",
        }
        danger: list[Pos] = []
        if telegraph == Telegraph.SLAM:
            danger = positions_in_radius(_center(board_size), 1, board_size)
        elif telegraph == Telegraph.SHRINK and boss.shrink_level < 1:
            depth = 0
            for x in range(board_size):
                for y in range(board_size):
                    if x <= depth or y <= depth or x >= board_size - 1 - depth or y >= board_size - 1 - depth:
                        danger.append(Pos(x, y))
        return TelegraphPreview(telegraph, messages.get(telegraph, ""), danger)

    def resolve_mechanic(
        self,
        telegraph: Telegraph,
        boss: BossState,
        board_size: int,
        rng: random.Random,
    ) -> tuple[list[Pos], list[str]]:
        logs: list[str] = []
        hazards: list[Pos] = []
        if telegraph == Telegraph.SLAM:
            hazards = positions_in_radius(_center(board_size), 1, board_size)
            logs.append("重击落下！")
        elif telegraph == Telegraph.EARTHQUAKE:
            center = Pos(rng.randint(1, board_size - 2), rng.randint(1, board_size - 2))
            hazards = positions_in_radius(center, 1, board_size)
            logs.append(f"地震发生在 ({center.x}, {center.y}) 附近！")
        elif telegraph == Telegraph.SHRINK:
            boss.shrink_level += 1
            depth = boss.shrink_level - 1
            for x in range(board_size):
                for y in range(board_size):
                    if x <= depth or y <= depth or x >= board_size - 1 - depth or y >= board_size - 1 - depth:
                        hazards.append(Pos(x, y))
            logs.append("外圈变为即死区！")
        elif telegraph == Telegraph.EARTHEN_FURY:
            if boss.fury_cast_turns > 0:
                boss.fury_cast_turns -= 1
                if boss.fury_cast_turns == 0:
                    logs.append("土神之怒发动！")
        return hazards, logs

    def mechanic_damage(self, telegraph: Telegraph) -> int:
        return {
            Telegraph.SLAM: 180,
            Telegraph.EARTHQUAKE: 130,
            Telegraph.EARTHEN_FURY: 9999,
        }.get(telegraph, 0)

    def basic_damage(self, boss: BossState) -> int:
        return {1: 120, 2: 150, 3: 180}.get(boss.phase, 120)

    def fury_name(self) -> str:
        return "土神之怒"

    def victory_message(self) -> str:
        return "胜利！土灵守护者被击败。"


class WindSovereignBoss:
    boss_id = "wind"

    def create(self) -> BossState:
        return BossState(name="风灵领主", hp=5000, max_hp=5000, boss_id=self.boss_id)

    def update_phase(self, boss: BossState) -> None:
        ratio = boss.hp_ratio
        if ratio <= 0.4:
            boss.phase = 3
        elif ratio <= 0.7:
            boss.phase = 2
        else:
            boss.phase = 1

    def pick_telegraph(self, boss: BossState, rng: random.Random) -> Telegraph:
        if boss.phase == 1:
            return Telegraph.GALE
        if boss.phase == 2:
            return Telegraph.SPREAD
        if boss.fury_cast_turns > 0:
            return Telegraph.CYCLONE
        return Telegraph.STACK

    def preview(self, telegraph: Telegraph, board_size: int, boss: BossState) -> TelegraphPreview:
        messages = {
            Telegraph.GALE: "Boss 预备风刃：Boss 前方直线高伤。",
            Telegraph.SPREAD: "Boss 预备分散：相邻友军将受重罚。",
            Telegraph.STACK: "Boss 预备集合：必须靠近棋盘中心。",
            Telegraph.CYCLONE: "Boss 读条「旋风」：2 回合内必须打断！",
        }
        danger: list[Pos] = []
        if telegraph == Telegraph.GALE:
            cx = board_size // 2
            for y in range(3, board_size):
                danger.append(Pos(cx, y))
        elif telegraph == Telegraph.STACK:
            danger = positions_in_radius(_center(board_size), 1, board_size)
        return TelegraphPreview(telegraph, messages.get(telegraph, ""), danger)

    def resolve_mechanic(
        self,
        telegraph: Telegraph,
        boss: BossState,
        board_size: int,
        rng: random.Random,
    ) -> tuple[list[Pos], list[str]]:
        logs: list[str] = []
        hazards: list[Pos] = []
        if telegraph == Telegraph.GALE:
            cx = board_size // 2
            for y in range(3, board_size):
                hazards.append(Pos(cx, y))
            logs.append("风刃扫过中央列！")
        elif telegraph == Telegraph.SPREAD:
            logs.append("分散判定：相邻友军受创！")
        elif telegraph == Telegraph.STACK:
            logs.append("集合判定：远离中心者受创！")
        elif telegraph == Telegraph.CYCLONE:
            if boss.fury_cast_turns > 0:
                boss.fury_cast_turns -= 1
                if boss.fury_cast_turns == 0:
                    logs.append("旋风发动！")
        return hazards, logs

    def mechanic_damage(self, telegraph: Telegraph) -> int:
        return {
            Telegraph.GALE: 150,
            Telegraph.SPREAD: 200,
            Telegraph.STACK: 220,
            Telegraph.CYCLONE: 9999,
        }.get(telegraph, 0)

    def basic_damage(self, boss: BossState) -> int:
        return {1: 100, 2: 130, 3: 160}.get(boss.phase, 100)

    def fury_name(self) -> str:
        return "旋风"

    def victory_message(self) -> str:
        return "胜利！风灵领主被击败。"


BOSS_PROFILES: dict[str, EarthGuardianBoss | WindSovereignBoss] = {
    "earth": EarthGuardianBoss(),
    "wind": WindSovereignBoss(),
}


def get_boss_profile(boss_id: str) -> EarthGuardianBoss | WindSovereignBoss:
    return BOSS_PROFILES.get(boss_id, BOSS_PROFILES["earth"])


def create_boss(boss_id: str = "earth") -> BossState:
    return get_boss_profile(boss_id).create()
