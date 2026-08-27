"""Tests for boss telegraphs."""

import random
import unittest

from sim.bosses import create_boss, get_boss_profile
from sim.types import Telegraph


class BossTests(unittest.TestCase):
    def test_earth_phase_thresholds(self) -> None:
        profile = get_boss_profile("earth")
        boss = create_boss("earth")
        boss.hp = 2800
        profile.update_phase(boss)
        self.assertEqual(boss.phase, 2)
        boss.hp = 1600
        profile.update_phase(boss)
        self.assertEqual(boss.phase, 3)

    def test_wind_phase_two_spread(self) -> None:
        profile = get_boss_profile("wind")
        boss = create_boss("wind")
        boss.hp = 3000
        profile.update_phase(boss)
        telegraph = profile.pick_telegraph(boss, random.Random(0))
        self.assertEqual(telegraph, Telegraph.SPREAD)

    def test_wind_preview_stack_marks_center(self) -> None:
        profile = get_boss_profile("wind")
        boss = create_boss("wind")
        preview = profile.preview(Telegraph.STACK, 7, boss)
        self.assertTrue(any(p.x == 3 and p.y == 3 for p in preview.danger_cells))

    def test_earth_slam_preview(self) -> None:
        profile = get_boss_profile("earth")
        boss = create_boss("earth")
        preview = profile.preview(Telegraph.SLAM, 7, boss)
        self.assertIn(Telegraph.SLAM, [preview.telegraph])
        self.assertGreater(len(preview.danger_cells), 0)

    def test_ice_phase_two_frozen_ground(self) -> None:
        profile = get_boss_profile("ice")
        boss = create_boss("ice")
        boss.hp = 3000
        profile.update_phase(boss)
        telegraph = profile.pick_telegraph(boss, random.Random(0))
        self.assertEqual(telegraph, Telegraph.FROZEN_GROUND)

    def test_ice_lance_preview_cross(self) -> None:
        profile = get_boss_profile("ice")
        boss = create_boss("ice")
        preview = profile.preview(Telegraph.ICE_LANCE, 7, boss)
        self.assertTrue(any(p.x == 3 and p.y == 2 for p in preview.danger_cells))
        self.assertTrue(any(p.x == 3 and p.y == 5 for p in preview.danger_cells))

    def test_ice_ring_preview_marks_non_ring(self) -> None:
        profile = get_boss_profile("ice")
        boss = create_boss("ice")
        preview = profile.preview(Telegraph.ICE_RING, 7, boss)
        self.assertTrue(any(p.x == 3 and p.y == 3 for p in preview.danger_cells))
        self.assertFalse(any(p.x == 3 and p.y == 1 for p in preview.danger_cells))


if __name__ == "__main__":
    unittest.main()
