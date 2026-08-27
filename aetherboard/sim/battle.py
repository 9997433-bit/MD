"""Deterministic battle state machine."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Optional

from .board import (
    apply_hazards,
    apply_shrink,
    clear_hazards,
    is_deadly,
    make_board,
    neighbors,
    positions_in_radius,
)
from .boss import (
    boss_basic_damage,
    boss_fury_damage,
    boss_quake_damage,
    boss_slam_damage,
    create_boss,
    earthquake_hazards,
    slam_targets,
    telegraph_for_phase,
    update_boss_phase,
    warning_message,
)
from .jobs import MOVE_RANGE, create_party, skill_for, unit_skills
from .skills import SKILLS
from .types import (
    ActionChoice,
    BattleLog,
    BattleState,
    BossState,
    CellKind,
    Phase,
    Pos,
    Telegraph,
    UnitState,
)


class BattleEngine:
    """Turn-based battle with FF14-inspired phase pacing."""

    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)
        self.state = self._new_state()

    def _new_state(self) -> BattleState:
        board = make_board()
        boss = create_boss()
        return BattleState(
            turn=1,
            phase=Phase.WARNING,
            board_size=7,
            cells=board,
            party=create_party(),
            boss=boss,
            log=BattleLog(),
        )

    def clone_state(self) -> BattleState:
        return deepcopy(self.state)

    def reset(self, seed: Optional[int] = None) -> BattleState:
        if seed is not None:
            self.rng = random.Random(seed)
        self.state = self._new_state()
        return self.state

    def unit_by_id(self, unit_id: str) -> UnitState:
        for unit in self.state.party:
            if unit.id == unit_id:
                return unit
        raise KeyError(unit_id)

    def living_party(self) -> list[UnitState]:
        return [u for u in self.state.party if u.alive]

    def party_damage_multiplier(self) -> float:
        if any(u.alive and u.bard_song_turns > 0 for u in self.state.party):
            return 1.2
        return 1.0

    def begin_warning(self) -> None:
        update_boss_phase(self.state.boss)
        telegraph = telegraph_for_phase(self.state.boss, self.rng)
        self.state.boss.telegraph = telegraph
        if telegraph == Telegraph.EARTHEN_FURY and self.state.boss.fury_cast_turns == 0:
            self.state.boss.fury_cast_turns = 2
        message = warning_message(telegraph)
        if message:
            self.state.log.add(f"[预警] {message}")
        self.state.phase = Phase.MOVE

    def can_move(self, unit_id: str, dest: Pos) -> bool:
        unit = self.unit_by_id(unit_id)
        if not unit.alive or unit.moved_this_turn:
            return False
        if not dest.in_bounds(self.state.board_size):
            return False
        if is_deadly(self.state.cells, dest):
            return False
        if dest == unit.pos:
            return False
        if any(u.alive and u.id != unit.id and u.pos == dest for u in self.state.party):
            return False
        max_range = MOVE_RANGE[unit.job]
        return unit.pos.distance(dest) <= max_range

    def move_unit(self, unit_id: str, dest: Pos) -> bool:
        if not self.can_move(unit_id, dest):
            return False
        unit = self.unit_by_id(unit_id)
        unit.pos = dest
        unit.moved_this_turn = True
        self.state.log.add(f"{unit.name} 移动到 ({dest.x}, {dest.y})。")
        return True

    def advance_after_moves(self) -> None:
        if self.state.phase == Phase.MOVE:
            self.state.phase = Phase.ACTION

    def can_use_skill(self, unit_id: str, skill_id: str, target: Optional[Pos] = None) -> bool:
        unit = self.unit_by_id(unit_id)
        if not unit.alive:
            return False
        skill = skill_for(unit, skill_id)
        if skill.kind == "gcd":
            if self.state.phase != Phase.ACTION or unit.gcd_used:
                return False
        else:
            if self.state.phase != Phase.WEAVE or unit.ogcd_used:
                return False
        if skill_id == "interrupt":
            return self.state.boss.fury_cast_turns > 0
        if skill_id not in unit_skills(unit):
            return False
        if skill.range == 0:
            return True
        if target is None:
            return False
        if skill.heal > 0:
            return any(u.alive and u.pos == target for u in self.state.party)
        return target.in_bounds(self.state.board_size)

    def use_skill(self, unit_id: str, skill_id: str, target: Optional[Pos] = None) -> bool:
        if not self.can_use_skill(unit_id, skill_id, target):
            return False
        unit = self.unit_by_id(unit_id)
        skill = SKILLS[skill_id]
        if skill.kind == "gcd":
            unit.gcd_used = True
        else:
            unit.ogcd_used = True

        if skill.heal > 0 and target is not None:
            self._apply_heal(unit, skill, target)
        elif skill_id == "interrupt":
            self.state.boss.fury_cast_turns = 0
            self.state.log.add(f"{unit.name} 打断了土神之怒！")
        elif skill_id in {"rampart", "manaward"}:
            unit.mit_turns = skill.mit_duration
            self.state.log.add(f"{unit.name} 获得 {skill.mit_duration} 回合减伤。")
        elif skill_id == "provoke":
            unit.taunt_turns = 1
            self.state.log.add(f"{unit.name} 挑衅 Boss，下回合优先承受攻击。")
        elif skill_id == "mages_ballad":
            unit.bard_song_turns = 3
            for ally in self.living_party():
                ally.bard_song_turns = 3
            self.state.log.add(f"{unit.name} 开启魔人歌，全队伤害提升。")
        elif skill_id == "repelling_shot":
            self._apply_damage(unit, skill, self.state.boss.pos if hasattr(self.state.boss, "pos") else Pos(3, 2))
            self._repel(unit)
        else:
            self._apply_party_offensive(unit, skill)

        return True

    def _boss_pos(self) -> Pos:
        return Pos(self.state.board_size // 2, 2)

    def _apply_party_offensive(self, unit: UnitState, skill) -> None:
        power = skill.power
        multiplier = self.party_damage_multiplier()
        if unit.job.value == "black_mage" and skill.id == "fire" and not unit.moved_this_turn:
            power = int(power * 1.5)
            self.state.log.add(f"{unit.name} 站桩读条，火炎伤害提升。")
        if unit.job.value == "bard" and skill.id == "straight_shot" and unit.bard_song_turns > 0:
            power = int(power * 1.3)
        damage = int(power * multiplier)
        self.state.boss.hp = max(0, self.state.boss.hp - damage)
        self.state.log.add(f"{unit.name} 使用 {skill.name}，造成 {damage} 点伤害。")
        if self.state.boss.hp == 0:
            self.state.boss.alive = False
            self.state.phase = Phase.VICTORY
            self.state.log.add("胜利！土灵守护者被击败。")

    def _apply_damage_to_unit(self, unit: UnitState, raw: int) -> None:
        damage = raw
        if unit.mit_turns > 0:
            damage = int(damage * 0.6)
        unit.hp = max(0, unit.hp - damage)
        if unit.hp == 0:
            unit.alive = False
            self.state.log.add(f"{unit.name} 倒下了。")

    def _apply_heal(self, unit: UnitState, skill, target: Pos) -> None:
        targets = []
        if skill.aoe_radius > 0:
            for ally in self.living_party():
                if ally.pos.distance(target) <= skill.aoe_radius:
                    targets.append(ally)
        else:
            targets = [u for u in self.living_party() if u.pos == target]
        for ally in targets:
            if skill.heal >= 9999:
                ally.hp = ally.max_hp
            else:
                ally.hp = min(ally.max_hp, ally.hp + skill.heal)
            self.state.log.add(f"{unit.name} 治疗 {ally.name}。")

    def _apply_damage(self, unit: UnitState, skill, target_pos: Pos) -> None:
        if skill.power > 0:
            damage = int(skill.power * self.party_damage_multiplier())
            self.state.boss.hp = max(0, self.state.boss.hp - damage)

    def _repel(self, unit: UnitState) -> None:
        boss = self._boss_pos()
        dx = unit.pos.x - boss.x
        dy = unit.pos.y - boss.y
        if dx == 0 and dy == 0:
            dy = 1
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        dest = Pos(unit.pos.x + step_x, unit.pos.y + step_y)
        if dest.in_bounds(self.state.board_size) and not is_deadly(self.state.cells, dest):
            if not any(u.alive and u.id != unit.id and u.pos == dest for u in self.state.party):
                unit.pos = dest
                self.state.log.add(f"{unit.name} 后跃到 ({dest.x}, {dest.y})。")

    def advance_after_actions(self) -> None:
        if self.state.phase == Phase.ACTION:
            self.state.phase = Phase.WEAVE

    def advance_after_weaves(self) -> None:
        if self.state.phase == Phase.WEAVE:
            self.state.phase = Phase.RESOLVE
            self.resolve_turn()

    def all_party_ready_for_phase(self) -> bool:
        living = self.living_party()
        if not living:
            return True
        if self.state.phase == Phase.MOVE:
            return all(u.moved_this_turn for u in living)
        if self.state.phase == Phase.ACTION:
            return all(u.gcd_used for u in living)
        if self.state.phase == Phase.WEAVE:
            return True
        return True

    def auto_fill_missing_actions(self) -> None:
        """Simple AI defaults for demo/testing."""
        for unit in self.living_party():
            if self.state.phase == Phase.MOVE and not unit.moved_this_turn:
                self.move_unit(unit.id, unit.pos)
            elif self.state.phase == Phase.ACTION and not unit.gcd_used:
                default = unit_skills(unit)[0]
                if unit.job.value == "white_mage":
                    wounded = min(self.living_party(), key=lambda u: u.hp / u.max_hp)
                    self.use_skill(unit.id, default, wounded.pos)
                else:
                    self.use_skill(unit.id, default, self._boss_pos())
            elif self.state.phase == Phase.WEAVE and not unit.ogcd_used:
                if self.state.boss.fury_cast_turns > 0 and unit.job.value == "bard":
                    self.use_skill(unit.id, "repelling_shot", self._boss_pos())
                elif unit.job.value == "knight" and unit.mit_turns == 0:
                    self.use_skill(unit.id, "rampart", unit.pos)
                else:
                    pass

    def resolve_turn(self) -> None:
        if self.state.phase != Phase.RESOLVE:
            return
        telegraph = self.state.boss.telegraph
        clear_hazards(self.state.cells, self.state.board_size)

        if telegraph == Telegraph.SLAM:
            for pos in slam_targets(self.state.board_size):
                for unit in self.living_party():
                    if unit.pos == pos:
                        self._apply_damage_to_unit(unit, boss_slam_damage())
        elif telegraph == Telegraph.EARTHQUAKE:
            hazards = earthquake_hazards(self.state.board_size, self.rng)
            self.state.pending_hazards = hazards
            apply_hazards(self.state.cells, hazards, self.state.board_size)
            for unit in self.living_party():
                if unit.pos in hazards:
                    self._apply_damage_to_unit(unit, boss_quake_damage())
        elif telegraph == Telegraph.SHRINK:
            self.state.boss.shrink_level += 1
            apply_shrink(self.state.cells, self.state.board_size, self.state.boss.shrink_level)
            self.state.log.add("外圈变为即死区！")
        elif telegraph == Telegraph.EARTHEN_FURY:
            if self.state.boss.fury_cast_turns > 0:
                self.state.boss.fury_cast_turns -= 1
                if self.state.boss.fury_cast_turns == 0:
                    for unit in self.living_party():
                        self._apply_damage_to_unit(unit, boss_fury_damage())

        tank = next((u for u in self.living_party() if u.job.value == "knight"), None)
        target = tank if tank and tank.taunt_turns > 0 else self.rng.choice(self.living_party()) if self.living_party() else None
        if target:
            self._apply_damage_to_unit(target, boss_basic_damage(self.state.boss))
            self.state.log.add(f"Boss 攻击 {target.name}。")

        for unit in self.living_party():
            if is_deadly(self.state.cells, unit.pos):
                unit.alive = False
                unit.hp = 0
                self.state.log.add(f"{unit.name} 站在即死区，被淘汰。")

        for unit in self.living_party():
            if unit.mit_turns > 0:
                unit.mit_turns -= 1
            if unit.taunt_turns > 0:
                unit.taunt_turns -= 1
            if unit.bard_song_turns > 0:
                unit.bard_song_turns -= 1
            unit.reset_turn_flags()

        if not self.living_party():
            self.state.phase = Phase.DEFEAT
            self.state.log.add("全队阵亡，战斗失败。")
            return

        if not self.state.boss.alive:
            self.state.phase = Phase.VICTORY
            return

        self.state.turn += 1
        self.state.boss.telegraph = Telegraph.NONE
        self.begin_warning()

    def step_auto(self) -> BattleState:
        """Run one full turn with default AI choices."""
        if self.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
            return self.state
        if self.state.phase == Phase.WARNING:
            self.begin_warning()
        while self.state.phase == Phase.MOVE:
            self.auto_fill_missing_actions()
            self.advance_after_moves()
        while self.state.phase == Phase.ACTION:
            self.auto_fill_missing_actions()
            if all(u.gcd_used or not u.alive for u in self.state.party):
                self.advance_after_actions()
                break
        if self.state.phase == Phase.WEAVE:
            self.auto_fill_missing_actions()
            self.advance_after_weaves()
        return self.state
