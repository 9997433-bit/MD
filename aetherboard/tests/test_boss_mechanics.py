"""Tests for boss telegraphs."""

import random
import unittest

from sim.boss import earthquake_hazards, telegraph_for_phase, update_boss_phase
from sim.types import BossState, Telegraph


class BossTests(unittest.TestCase):
    def test_phase_thresholds(self) -> None:
        boss = BossState(name="test", hp=3000, max_hp=6000)
        update_boss_phase(boss)
        self.assertEqual(boss.phase, 2)
        boss.hp = 2000
        update_boss_phase(boss)
        self.assertEqual(boss.phase, 3)

    def test_phase_one_telegraph(self) -> None:
        boss = BossState(name="test", hp=6000, max_hp=6000, phase=1)
        telegraph = telegraph_for_phase(boss, random.Random(0))
        self.assertEqual(telegraph, Telegraph.SLAM)

    def test_earthquake_hazards_in_bounds(self) -> None:
        rng = random.Random(3)
        hazards = earthquake_hazards(7, rng)
        self.assertGreater(len(hazards), 0)
        for pos in hazards:
            self.assertTrue(pos.in_bounds(7))


if __name__ == "__main__":
    unittest.main()
