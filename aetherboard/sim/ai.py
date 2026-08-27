"""Tactical AI for movement and skill selection."""

from __future__ import annotations

from .board import is_deadly
from .jobs import MOVE_RANGE, unit_skills
from .types import Pos, Telegraph, UnitState


def boss_center(board_size: int) -> Pos:
    return Pos(board_size // 2, 2)


def board_center(board_size: int) -> Pos:
    return Pos(board_size // 2, board_size // 2)


def reachable_positions(unit: UnitState, state, occupied: set[tuple[int, int]]) -> list[Pos]:
    start = unit.pos
    max_range = MOVE_RANGE[unit.job]
    results: list[Pos] = []
    for x in range(state.board_size):
        for y in range(state.board_size):
            dest = Pos(x, y)
            if dest == start:
                results.append(dest)
                continue
            if not dest.in_bounds(state.board_size):
                continue
            if is_deadly(state.cells, dest):
                continue
            if (x, y) in occupied and (x, y) != (start.x, start.y):
                continue
            if dest == boss_center(state.board_size):
                continue
            if start.distance(dest) <= max_range:
                results.append(dest)
    return results


def _min_dist_to_others(unit: UnitState, pos: Pos, party: list[UnitState]) -> int:
    others = [u for u in party if u.alive and u.id != unit.id]
    if not others:
        return 99
    return min(pos.distance(u.pos) for u in others)


def _edge_penalty(pos: Pos, board_size: int) -> int:
    penalty = 0
    if pos.x <= 0 or pos.x >= board_size - 1 or pos.y <= 0 or pos.y >= board_size - 1:
        penalty -= 40
    elif pos.x <= 1 or pos.x >= board_size - 2 or pos.y <= 1 or pos.y >= board_size - 2:
        penalty -= 15
    return penalty


def score_position(unit: UnitState, pos: Pos, state) -> int:
    telegraph = state.boss.telegraph
    center = board_center(state.board_size)
    boss = boss_center(state.board_size)
    score = _edge_penalty(pos, state.board_size)
    party = [u for u in state.party if u.alive]

    if telegraph == Telegraph.SLAM:
        score += pos.distance(center) * 3
    elif telegraph == Telegraph.EARTHQUAKE:
        if any(p.x == pos.x and p.y == pos.y for p in state.pending_hazards):
            score -= 80
        score += pos.distance(center) * 2
    elif telegraph == Telegraph.SHRINK:
        score += pos.distance(center) * 4
        if pos.y >= state.board_size - 1 or pos.x <= 0 or pos.x >= state.board_size - 1:
            score -= 40
        if pos.y >= state.board_size - 2:
            score -= 25
    elif telegraph == Telegraph.SPREAD:
        score += _min_dist_to_others(unit, pos, party) * 5
    elif telegraph == Telegraph.STACK:
        score -= pos.distance(center) * 4
    elif telegraph == Telegraph.GALE:
        if pos.x == boss.x:
            score -= 10
        score += pos.distance(boss) * 2
    elif telegraph == Telegraph.ICE_LANCE:
        if pos.x == boss.x or pos.y == boss.y:
            score -= 60
    elif telegraph == Telegraph.FROZEN_GROUND:
        if any(p.x == pos.x and p.y == pos.y for p in state.pending_hazards):
            score -= 80
    elif telegraph == Telegraph.ICE_RING:
        if pos.distance(center) == 2:
            score += 40
        else:
            score -= 30
    else:
        score += _min_dist_to_others(unit, pos, party)

    if is_deadly(state.cells, pos):
        score -= 1000
    if unit.job.value == "black_mage" and pos != unit.pos:
        score -= 2
    if unit.job.value == "knight" and telegraph != Telegraph.SPREAD:
        score -= pos.distance(boss) * 2
    return score


def pick_move_dest(unit: UnitState, state) -> Pos:
    occupied = {(u.pos.x, u.pos.y) for u in state.party if u.alive and u.id != unit.id}
    options = reachable_positions(unit, state, occupied)
    if not options:
        return unit.pos
    return max(options, key=lambda p: score_position(unit, p, state))


def pick_gcd_target(unit: UnitState, state) -> Pos | None:
    if unit.job.value == "white_mage":
        wounded = min(
            [u for u in state.party if u.alive],
            key=lambda u: u.hp / u.max_hp,
        )
        if wounded.hp / wounded.max_hp < 0.85:
            return wounded.pos
        return wounded.pos
    return boss_center(state.board_size)


def pick_gcd_skill(unit: UnitState, state) -> str:
    skills = unit_skills(unit)
    if unit.job.value == "white_mage":
        low = min(u.hp / u.max_hp for u in state.party if u.alive)
        if low < 0.45:
            return "medica"
        return "cure"
    if unit.job.value == "black_mage" and not unit.moved_this_turn:
        return "fire"
    return skills[0]


def pick_ogcd(unit: UnitState, state) -> tuple[str, Pos | None] | None:
    if state.boss.fury_cast_turns > 0:
        return "interrupt", boss_center(state.board_size)
    if unit.job.value == "knight" and unit.mit_turns == 0 and state.boss.phase >= 2:
        return "rampart", unit.pos
    if unit.job.value == "white_mage":
        low = min((u for u in state.party if u.alive), key=lambda u: u.hp / u.max_hp)
        if low.hp / low.max_hp < 0.35:
            return "benediction", low.pos
    if unit.job.value == "black_mage" and unit.mit_turns == 0:
        return "manaward", unit.pos
    if unit.job.value == "bard" and not any(u.bard_song_turns > 0 for u in state.party if u.alive):
        return "mages_ballad", unit.pos
    if unit.job.value == "knight" and state.boss.phase >= 2:
        return "provoke", boss_center(state.board_size)
    return None
