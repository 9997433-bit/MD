"""Shared battle types for Aetherboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class Phase(Enum):
    WARNING = auto()
    MOVE = auto()
    ACTION = auto()
    WEAVE = auto()
    RESOLVE = auto()
    VICTORY = auto()
    DEFEAT = auto()


class Job(Enum):
    KNIGHT = "knight"
    WHITE_MAGE = "white_mage"
    BLACK_MAGE = "black_mage"
    BARD = "bard"


class CellKind(Enum):
    NORMAL = auto()
    HAZARD = auto()
    SAFE = auto()


class Telegraph(Enum):
    NONE = auto()
    SLAM = auto()
    EARTHQUAKE = auto()
    SHRINK = auto()
    EARTHEN_FURY = auto()
    GALE = auto()
    SPREAD = auto()
    STACK = auto()
    CYCLONE = auto()
    ICE_LANCE = auto()
    FROZEN_GROUND = auto()
    ICE_RING = auto()
    BLIZZARD = auto()


class BossId(Enum):
    EARTH = "earth"
    WIND = "wind"
    ICE = "ice"


@dataclass(frozen=True)
class Pos:
    x: int
    y: int

    def distance(self, other: Pos) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def in_bounds(self, size: int = 7) -> bool:
        return 0 <= self.x < size and 0 <= self.y < size


@dataclass
class SkillDef:
    id: str
    name: str
    kind: str  # "gcd" | "ogcd"
    range: int
    power: int
    description: str
    aoe_radius: int = 0
    heal: int = 0
    mit_duration: int = 0


@dataclass
class UnitState:
    id: str
    name: str
    job: Job
    pos: Pos
    hp: int
    max_hp: int
    alive: bool = True
    moved_this_turn: bool = False
    gcd_used: bool = False
    ogcd_used: bool = False
    casting: bool = False
    mit_turns: int = 0
    bard_song_turns: int = 0
    taunt_turns: int = 0

    def reset_turn_flags(self) -> None:
        self.moved_this_turn = False
        self.gcd_used = False
        self.ogcd_used = False
        self.casting = False


@dataclass
class BossState:
    name: str
    hp: int
    max_hp: int
    boss_id: str = "earth"
    phase: int = 1
    telegraph: Telegraph = Telegraph.NONE
    fury_cast_turns: int = 0
    shrink_level: int = 0
    alive: bool = True

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp if self.max_hp else 0.0


@dataclass
class BattleLog:
    entries: list[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        self.entries.append(message)


@dataclass
class ActionChoice:
    unit_id: str
    action: str
    target: Optional[Pos] = None


@dataclass
class BattleState:
    turn: int
    phase: Phase
    board_size: int
    cells: list[list[CellKind]]
    party: list[UnitState]
    boss: BossState
    log: BattleLog = field(default_factory=BattleLog)
    pending_hazards: list[Pos] = field(default_factory=list)
