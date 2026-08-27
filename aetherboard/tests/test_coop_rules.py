"""Coop ownership and host enforcement tests."""

from __future__ import annotations

import unittest

from scripts.battle_host import BattleHost
from sim.coop_rules import can_control


class CoopRulesTests(unittest.TestCase):
    def test_p1_units(self) -> None:
        self.assertTrue(can_control(1, "knight", True))
        self.assertFalse(can_control(2, "knight", True))

    def test_host_rejects_wrong_player(self) -> None:
        host = BattleHost(coop=True)
        ok, err = host.apply_command(
            {
                "type": "Move",
                "unitId": "knight",
                "playerId": 2,
                "targetX": 3,
                "targetY": 6,
            }
        )
        self.assertFalse(ok)
        self.assertIn("无权", err or "")


if __name__ == "__main__":
    unittest.main()
