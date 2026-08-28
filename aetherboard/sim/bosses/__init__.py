"""Boss profile protocol and registry."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from ..board import (
    positions_at_distance,
    positions_diagonals,
    positions_in_radius,
    positions_2x2,
)
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


class IceEmpressBoss:
    boss_id = "ice"

    def create(self) -> BossState:
        return BossState(name="冰灵女皇", hp=4800, max_hp=4800, boss_id=self.boss_id)

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
            return Telegraph.ICE_LANCE
        if boss.phase == 2:
            return Telegraph.FROZEN_GROUND
        if boss.fury_cast_turns > 0:
            return Telegraph.BLIZZARD
        if boss.shrink_level < 1:
            return Telegraph.ICE_RING
        return Telegraph.BLIZZARD

    def preview(self, telegraph: Telegraph, board_size: int, boss: BossState) -> TelegraphPreview:
        messages = {
            Telegraph.ICE_LANCE: "Boss 预备冰枪：十字路径高伤。",
            Telegraph.FROZEN_GROUND: "Boss 预备霜冻：2×2 危险区。",
            Telegraph.ICE_RING: "Boss 预备冰环：必须站在距离中心 2 格的环上。",
            Telegraph.BLIZZARD: "Boss 读条「暴雪」：2 回合内必须打断！",
        }
        danger: list[Pos] = []
        boss_pos = Pos(board_size // 2, 2)
        center = _center(board_size)
        if telegraph == Telegraph.ICE_LANCE:
            for x in range(board_size):
                danger.append(Pos(x, boss_pos.y))
            for y in range(board_size):
                p = Pos(boss_pos.x, y)
                if p not in danger:
                    danger.append(p)
        elif telegraph == Telegraph.ICE_RING:
            ring = set(positions_at_distance(center, 2, board_size))
            for x in range(board_size):
                for y in range(board_size):
                    p = Pos(x, y)
                    if p not in ring:
                        danger.append(p)
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
        boss_pos = Pos(board_size // 2, 2)
        if telegraph == Telegraph.ICE_LANCE:
            for x in range(board_size):
                hazards.append(Pos(x, boss_pos.y))
            for y in range(board_size):
                p = Pos(boss_pos.x, y)
                if p not in hazards:
                    hazards.append(p)
            logs.append("冰枪十字扫过棋盘！")
        elif telegraph == Telegraph.FROZEN_GROUND:
            logs.append("霜冻区域爆发！")
        elif telegraph == Telegraph.ICE_RING:
            boss.shrink_level += 1
            logs.append("冰环收缩：未站在环上者受创！")
        elif telegraph == Telegraph.BLIZZARD:
            if boss.fury_cast_turns > 0:
                boss.fury_cast_turns -= 1
                if boss.fury_cast_turns == 0:
                    logs.append("暴雪发动！")
        return hazards, logs

    def mechanic_damage(self, telegraph: Telegraph) -> int:
        return {
            Telegraph.ICE_LANCE: 160,
            Telegraph.FROZEN_GROUND: 140,
            Telegraph.ICE_RING: 210,
            Telegraph.BLIZZARD: 9999,
        }.get(telegraph, 0)

    def basic_damage(self, boss: BossState) -> int:
        return {1: 110, 2: 140, 3: 170}.get(boss.phase, 110)

    def fury_name(self) -> str:
        return "暴雪"

    def victory_message(self) -> str:
        return "胜利！冰灵女皇被击败。"


class FireSovereignBoss:
    boss_id = "fire"

    def create(self) -> BossState:
        return BossState(name="火灵君主", hp=5200, max_hp=5200, boss_id=self.boss_id)

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
            return Telegraph.FLAME_BREATH
        if boss.phase == 2:
            return Telegraph.METEOR
        if boss.fury_cast_turns > 0:
            return Telegraph.ERUPTION
        if boss.shrink_level < 1:
            return Telegraph.HEAT_LINK
        return Telegraph.ERUPTION

    def preview(self, telegraph: Telegraph, board_size: int, boss: BossState) -> TelegraphPreview:
        messages = {
            Telegraph.FLAME_BREATH: "Boss 预备火息：对角线 X 路径高伤。",
            Telegraph.METEOR: "Boss 预备陨石：随机落点危险区。",
            Telegraph.HEAT_LINK: "Boss 预备灼热连结：必须与友军相邻。",
            Telegraph.ERUPTION: "Boss 读条「喷发」：2 回合内必须打断！",
        }
        danger: list[Pos] = []
        if telegraph == Telegraph.FLAME_BREATH:
            danger = positions_diagonals(_center(board_size), board_size)
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
        if telegraph == Telegraph.FLAME_BREATH:
            hazards = positions_diagonals(_center(board_size), board_size)
            logs.append("火息沿对角线扫过！")
        elif telegraph == Telegraph.METEOR:
            logs.append("陨石砸落！")
        elif telegraph == Telegraph.HEAT_LINK:
            boss.shrink_level += 1
            logs.append("灼热连结：孤身者受创！")
        elif telegraph == Telegraph.ERUPTION:
            if boss.fury_cast_turns > 0:
                boss.fury_cast_turns -= 1
                if boss.fury_cast_turns == 0:
                    logs.append("喷发发动！")
        return hazards, logs

    def mechanic_damage(self, telegraph: Telegraph) -> int:
        return {
            Telegraph.FLAME_BREATH: 155,
            Telegraph.METEOR: 150,
            Telegraph.HEAT_LINK: 200,
            Telegraph.ERUPTION: 9999,
        }.get(telegraph, 0)

    def basic_damage(self, boss: BossState) -> int:
        return {1: 115, 2: 145, 3: 175}.get(boss.phase, 115)

    def fury_name(self) -> str:
        return "喷发"

    def victory_message(self) -> str:
        return "胜利！火灵君主被击败。"


BOSS_PROFILES: dict[
    str, EarthGuardianBoss | WindSovereignBoss | IceEmpressBoss | FireSovereignBoss
] = {
    "earth": EarthGuardianBoss(),
    "wind": WindSovereignBoss(),
    "ice": IceEmpressBoss(),
    "fire": FireSovereignBoss(),
}


def get_boss_profile(
    boss_id: str,
) -> EarthGuardianBoss | WindSovereignBoss | IceEmpressBoss | FireSovereignBoss:
    return BOSS_PROFILES.get(boss_id, BOSS_PROFILES["earth"])


def create_boss(boss_id: str = "earth") -> BossState:
    return get_boss_profile(boss_id).create()
