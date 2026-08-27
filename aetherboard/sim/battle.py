"""Deterministic battle state machine."""

from __future__ import annotations

import random
from copy import deepcopy
from typing import Optional

from .ai import pick_gcd_skill, pick_gcd_target, pick_move_dest, pick_ogcd, boss_center
from .board import apply_hazards, clear_hazards, is_deadly, make_board, positions_2x2, positions_in_radius
from .bosses import create_boss, get_boss_profile
from .jobs import create_party, skill_for, unit_skills
from .skills import SKILLS
from .types import (
    BattleLog,
    BattleState,
    CellKind,
    Phase,
    Pos,
    Telegraph,
    UnitState,
)


class BattleEngine:
    """Turn-based battle with FF14-inspired phase pacing."""

    def __init__(self, seed: int = 7, boss_id: str = "earth") -> None:
        self.rng = random.Random(seed)
        self.boss_id = boss_id
        self.profile = get_boss_profile(boss_id)
        self.state = self._new_state()

    def _new_state(self) -> BattleState:
        return BattleState(
            turn=1,
            phase=Phase.WARNING,
            board_size=7,
            cells=make_board(),
            party=create_party(),
            boss=create_boss(self.boss_id),
            log=BattleLog(),
        )

    def clone_state(self) -> BattleState:
        return deepcopy(self.state)

    def reset(self, seed: Optional[int] = None, boss_id: Optional[str] = None) -> BattleState:
        if seed is not None:
            self.rng = random.Random(seed)
        if boss_id is not None:
            self.boss_id = boss_id
            self.profile = get_boss_profile(boss_id)
        self.state = self._new_state()
        self.begin_warning()
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

    def telegraph_preview(self) -> list[Pos]:
        preview = self.profile.preview(
            self.state.boss.telegraph, self.state.board_size, self.state.boss
        )
        return preview.danger_cells

    def begin_warning(self) -> None:
        if self.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
            return
        self.profile.update_phase(self.state.boss)
        telegraph = self.profile.pick_telegraph(self.state.boss, self.rng)
        self.state.boss.telegraph = telegraph
        if telegraph in {Telegraph.EARTHEN_FURY, Telegraph.CYCLONE, Telegraph.BLIZZARD} and self.state.boss.fury_cast_turns == 0:
            self.state.boss.fury_cast_turns = 2
        self.state.pending_hazards = self._pending_mechanic_cells(telegraph)
        preview = self.profile.preview(telegraph, self.state.board_size, self.state.boss)
        danger = self.state.pending_hazards or preview.danger_cells
        if preview.message:
            self.state.log.add(f"[预警] {preview.message}")
        if telegraph == Telegraph.EARTHQUAKE and self.state.pending_hazards:
            center = self.state.pending_hazards[len(self.state.pending_hazards) // 2]
            self.state.log.add(f"[预警] 地震中心约在 ({center.x}, {center.y})。")
        if telegraph == Telegraph.FROZEN_GROUND and self.state.pending_hazards:
            center = self.state.pending_hazards[0]
            self.state.log.add(f"[预警] 霜冻区域约在 ({center.x}, {center.y}) 附近。")
        self.state.phase = Phase.MOVE

    def _pending_mechanic_cells(self, telegraph: Telegraph) -> list[Pos]:
        size = self.state.board_size
        if telegraph == Telegraph.EARTHQUAKE:
            center = Pos(self.rng.randint(1, size - 2), self.rng.randint(1, size - 2))
            return positions_in_radius(center, 1, size)
        if telegraph == Telegraph.FROZEN_GROUND:
            top_left = Pos(self.rng.randint(1, size - 3), self.rng.randint(1, size - 3))
            return positions_2x2(top_left, size)
        preview = self.profile.preview(telegraph, size, self.state.boss)
        return preview.danger_cells

    def can_move(self, unit_id: str, dest: Pos) -> bool:
        unit = self.unit_by_id(unit_id)
        if not unit.alive or unit.moved_this_turn or self.state.phase != Phase.MOVE:
            return False
        if not dest.in_bounds(self.state.board_size):
            return False
        if is_deadly(self.state.cells, dest):
            return False
        if dest == unit.pos:
            return False
        if dest == self._boss_pos():
            return False
        if any(u.alive and u.id != unit.id and u.pos == dest for u in self.state.party):
            return False
        from .jobs import MOVE_RANGE

        return unit.pos.distance(dest) <= MOVE_RANGE[unit.job]

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

    def end_phase(self) -> None:
        if self.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
            return
        self.auto_fill_missing_actions()
        if self.state.phase == Phase.MOVE:
            self.advance_after_moves()
        elif self.state.phase == Phase.ACTION:
            self.advance_after_actions()
        elif self.state.phase == Phase.WEAVE:
            self.advance_after_weaves()

    def can_use_skill(self, unit_id: str, skill_id: str, target: Optional[Pos] = None) -> bool:
        unit = self.unit_by_id(unit_id)
        if not unit.alive:
            return False
        if skill_id == "interrupt":
            if self.state.phase != Phase.WEAVE or unit.ogcd_used:
                return False
            return self.state.boss.fury_cast_turns > 0
        skill = skill_for(unit, skill_id)
        if skill.kind == "gcd":
            if self.state.phase != Phase.ACTION or unit.gcd_used:
                return False
        elif self.state.phase != Phase.WEAVE or unit.ogcd_used:
            return False
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
            self.state.boss.fury_cast_turns = -1
            self.state.log.add(f"{unit.name} 打断了{self.profile.fury_name()}！")
        elif skill_id in {"rampart", "manaward"}:
            unit.mit_turns = skill.mit_duration
            self.state.log.add(f"{unit.name} 获得 {skill.mit_duration} 回合减伤。")
        elif skill_id == "provoke":
            unit.taunt_turns = 1
            self.state.log.add(f"{unit.name} 挑衅 Boss。")
        elif skill_id == "mages_ballad":
            for ally in self.living_party():
                ally.bard_song_turns = 3
            self.state.log.add(f"{unit.name} 开启魔人歌。")
        elif skill_id == "repelling_shot":
            self._apply_boss_damage(int(skill.power * self.party_damage_multiplier()))
            self._repel(unit)
        else:
            self._apply_party_offensive(unit, skill)

        return True

    def _boss_pos(self) -> Pos:
        return boss_center(self.state.board_size)

    def _apply_party_offensive(self, unit: UnitState, skill) -> None:
        power = skill.power
        if unit.job.value == "black_mage" and skill.id == "fire" and not unit.moved_this_turn:
            power = int(power * 1.5)
            self.state.log.add(f"{unit.name} 站桩读条，火炎强化。")
        if unit.job.value == "bard" and skill.id == "straight_shot" and unit.bard_song_turns > 0:
            power = int(power * 1.3)
        damage = int(power * self.party_damage_multiplier())
        self._apply_boss_damage(damage)
        self.state.log.add(f"{unit.name} 使用 {skill.name}，造成 {damage} 点伤害。")

    def _apply_boss_damage(self, damage: int) -> None:
        self.state.boss.hp = max(0, self.state.boss.hp - damage)
        if self.state.boss.hp == 0:
            self.state.boss.alive = False
            self.state.phase = Phase.VICTORY
            self.state.log.add(self.profile.victory_message())

    def _apply_damage_to_unit(self, unit: UnitState, raw: int) -> None:
        damage = int(raw * 0.6) if unit.mit_turns > 0 else raw
        unit.hp = max(0, unit.hp - damage)
        if unit.hp == 0:
            unit.alive = False
            self.state.log.add(f"{unit.name} 倒下了。")

    def _apply_heal(self, unit: UnitState, skill, target: Pos) -> None:
        if skill.aoe_radius > 0:
            targets = [
                u for u in self.living_party() if u.pos.distance(target) <= skill.aoe_radius
            ]
        else:
            targets = [u for u in self.living_party() if u.pos == target]
        for ally in targets:
            ally.hp = ally.max_hp if skill.heal >= 9999 else min(ally.max_hp, ally.hp + skill.heal)
            self.state.log.add(f"{unit.name} 治疗 {ally.name}。")

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

    def advance_after_actions(self) -> None:
        if self.state.phase == Phase.ACTION:
            self.state.phase = Phase.WEAVE

    def advance_after_weaves(self) -> None:
        if self.state.phase == Phase.WEAVE:
            self.state.phase = Phase.RESOLVE
            self.resolve_turn()

    def auto_fill_missing_actions(self) -> None:
        if self.state.phase == Phase.WEAVE and self.state.boss.fury_cast_turns > 0:
            knight = next(
                (u for u in self.living_party() if u.job.value == "knight" and not u.ogcd_used),
                None,
            )
            if knight:
                self.use_skill(knight.id, "interrupt", self._boss_pos())

        for unit in self.living_party():
            if self.state.phase == Phase.MOVE and not unit.moved_this_turn:
                dest = pick_move_dest(unit, self.state)
                if dest != unit.pos:
                    self.move_unit(unit.id, dest)
                else:
                    unit.moved_this_turn = True
            elif self.state.phase == Phase.ACTION and not unit.gcd_used:
                skill_id = pick_gcd_skill(unit, self.state)
                target = pick_gcd_target(unit, self.state)
                self.use_skill(unit.id, skill_id, target)
            elif self.state.phase == Phase.WEAVE and not unit.ogcd_used:
                choice = pick_ogcd(unit, self.state)
                if choice:
                    skill_id, target = choice
                    self.use_skill(unit.id, skill_id, target)

    def _resolve_spread(self) -> None:
        living = self.living_party()
        damage = self.profile.mechanic_damage(Telegraph.SPREAD)
        hit: set[str] = set()
        for i, a in enumerate(living):
            for b in living[i + 1 :]:
                if a.pos.distance(b.pos) <= 1:
                    hit.add(a.id)
                    hit.add(b.id)
        for unit in living:
            if unit.id in hit:
                self._apply_damage_to_unit(unit, damage)
                self.state.log.add(f"{unit.name} 未能分散，受到 {damage} 伤害。")

    def _resolve_stack(self) -> None:
        center = Pos(self.state.board_size // 2, self.state.board_size // 2)
        damage = self.profile.mechanic_damage(Telegraph.STACK)
        for unit in self.living_party():
            if unit.pos.distance(center) > 1:
                self._apply_damage_to_unit(unit, damage)
                self.state.log.add(f"{unit.name} 未能集合，受到 {damage} 伤害。")

    def _resolve_ice_ring(self) -> None:
        center = Pos(self.state.board_size // 2, self.state.board_size // 2)
        damage = self.profile.mechanic_damage(Telegraph.ICE_RING)
        for unit in self.living_party():
            if unit.pos.distance(center) != 2:
                self._apply_damage_to_unit(unit, damage)
                self.state.log.add(f"{unit.name} 未站在冰环上，受到 {damage} 伤害。")

    def resolve_turn(self) -> None:
        if self.state.phase != Phase.RESOLVE:
            return
        telegraph = self.state.boss.telegraph
        clear_hazards(self.state.cells, self.state.board_size)

        hazards, logs = self.profile.resolve_mechanic(
            telegraph, self.state.boss, self.state.board_size, self.rng
        )
        if telegraph == Telegraph.EARTHQUAKE and self.state.pending_hazards:
            hazards = list(self.state.pending_hazards)
        if telegraph == Telegraph.FROZEN_GROUND and self.state.pending_hazards:
            hazards = list(self.state.pending_hazards)
        for entry in logs:
            self.state.log.add(entry)

        if hazards and telegraph in {Telegraph.SHRINK, Telegraph.EARTHQUAKE, Telegraph.FROZEN_GROUND}:
            apply_hazards(self.state.cells, hazards, self.state.board_size)
            mech_dmg = self.profile.mechanic_damage(telegraph)
            if mech_dmg > 0 and telegraph not in {Telegraph.SPREAD, Telegraph.STACK}:
                for unit in self.living_party():
                    if unit.pos in hazards:
                        self._apply_damage_to_unit(unit, mech_dmg)

        if telegraph == Telegraph.EARTHEN_FURY and self.state.boss.fury_cast_turns == 0:
            for unit in self.living_party():
                self._apply_damage_to_unit(unit, self.profile.mechanic_damage(telegraph))
        if telegraph == Telegraph.CYCLONE and self.state.boss.fury_cast_turns == 0:
            for unit in self.living_party():
                self._apply_damage_to_unit(unit, self.profile.mechanic_damage(telegraph))
        if telegraph == Telegraph.BLIZZARD and self.state.boss.fury_cast_turns == 0:
            for unit in self.living_party():
                self._apply_damage_to_unit(unit, self.profile.mechanic_damage(telegraph))

        if telegraph == Telegraph.SPREAD:
            self._resolve_spread()
        elif telegraph == Telegraph.STACK:
            self._resolve_stack()
        elif telegraph == Telegraph.ICE_RING:
            self._resolve_ice_ring()

        tank = next((u for u in self.living_party() if u.job.value == "knight"), None)
        if self.living_party():
            target = tank if tank and tank.taunt_turns > 0 else self.rng.choice(self.living_party())
            self._apply_damage_to_unit(target, self.profile.basic_damage(self.state.boss))
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
        if self.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
            return self.state
        if self.state.phase == Phase.WARNING:
            self.begin_warning()
        while self.state.phase == Phase.MOVE:
            self.auto_fill_missing_actions()
            if all(u.moved_this_turn or not u.alive for u in self.state.party):
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
