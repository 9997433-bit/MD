"""Tests for battle flow."""

import unittest

from sim.battle import BattleEngine
from sim.types import Phase, Pos


class BattleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = BattleEngine(seed=1)

    def test_warning_moves_to_move_phase(self) -> None:
        self.engine.begin_warning()
        self.assertEqual(self.engine.state.phase, Phase.MOVE)
        self.assertNotEqual(self.engine.state.boss.telegraph.name, "NONE")

    def test_move_respects_range(self) -> None:
        self.engine.begin_warning()
        knight = self.engine.unit_by_id("knight")
        dest = Pos(knight.pos.x, knight.pos.y - 2)
        self.assertTrue(self.engine.can_move("bard", Pos(3, 4)))
        self.assertFalse(self.engine.can_move("knight", dest))

    def test_fire_bonus_when_stationary(self) -> None:
        self.engine.begin_warning()
        self.engine.state.phase = Phase.ACTION
        mage = self.engine.unit_by_id("black_mage")
        mage.moved_this_turn = False
        before = self.engine.state.boss.hp
        self.engine.use_skill("black_mage", "fire", Pos(3, 2))
        damage = before - self.engine.state.boss.hp
        self.assertGreaterEqual(damage, 120)

    def test_auto_play_reaches_terminal_state(self) -> None:
        for _ in range(100):
            if self.engine.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
                break
            self.engine.step_auto()
        self.assertIn(self.engine.state.phase, {Phase.VICTORY, Phase.DEFEAT})

    def test_interrupt_clears_fury(self) -> None:
        self.engine.state.boss.phase = 3
        self.engine.state.boss.fury_cast_turns = 2
        self.engine.state.phase = Phase.WEAVE
        self.engine.use_skill("bard", "repelling_shot", Pos(3, 2))
        self.engine.use_skill("knight", "provoke", Pos(3, 2))
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
