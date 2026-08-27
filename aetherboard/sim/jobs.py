"""Party unit definitions."""

from __future__ import annotations

from .skills import SKILLS
from .types import Job, Pos, UnitState


def create_party() -> list[UnitState]:
    return [
        UnitState(
            id="knight",
            name="铁卫",
            job=Job.KNIGHT,
            pos=Pos(3, 5),
            hp=1200,
            max_hp=1200,
        ),
        UnitState(
            id="white_mage",
            name="白愈",
            job=Job.WHITE_MAGE,
            pos=Pos(2, 5),
            hp=900,
            max_hp=900,
        ),
        UnitState(
            id="black_mage",
            name="黑炎",
            job=Job.BLACK_MAGE,
            pos=Pos(4, 5),
            hp=800,
            max_hp=800,
        ),
        UnitState(
            id="bard",
            name="游弦",
            job=Job.BARD,
            pos=Pos(3, 4),
            hp=850,
            max_hp=850,
        ),
    ]


MOVE_RANGE = {
    Job.KNIGHT: 1,
    Job.WHITE_MAGE: 1,
    Job.BLACK_MAGE: 1,
    Job.BARD: 2,
}


def unit_skills(unit: UnitState) -> list[str]:
    mapping = {
        Job.KNIGHT: ["shield_bash", "rampart", "provoke"],
        Job.WHITE_MAGE: ["cure", "medica", "benediction"],
        Job.BLACK_MAGE: ["fire", "blizzard", "manaward"],
        Job.BARD: ["straight_shot", "mages_ballad", "repelling_shot"],
    }
    return mapping[unit.job]


def skill_for(unit: UnitState, skill_id: str):
    return SKILLS[skill_id]
