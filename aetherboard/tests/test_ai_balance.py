"""Tests for tactical AI and balance."""

import unittest

from sim.battle import BattleEngine
from sim.types import Phase


class AIBalanceTests(unittest.TestCase):
    def test_smart_auto_can_win_earth(self) -> None:
        wins = 0
        for seed in range(20):
            engine = BattleEngine(seed=seed, boss_id="earth")
            engine.begin_warning()
            for _ in range(80):
                if engine.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
                    break
                engine.step_auto()
            if engine.state.phase == Phase.VICTORY:
                wins += 1
        self.assertGreater(wins, 0)

    def test_smart_auto_can_win_wind(self) -> None:
        wins = 0
        for seed in range(20):
            engine = BattleEngine(seed=seed, boss_id="wind")
            engine.begin_warning()
            for _ in range(80):
                if engine.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
                    break
                engine.step_auto()
            if engine.state.phase == Phase.VICTORY:
                wins += 1
        self.assertGreater(wins, 0)


if __name__ == "__main__":
    unittest.main()
