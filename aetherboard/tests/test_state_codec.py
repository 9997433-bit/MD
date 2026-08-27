"""Tests for state JSON export."""

import unittest

from sim.battle import BattleEngine
from sim.state_codec import state_to_dict


class StateCodecTests(unittest.TestCase):
    def test_export_has_required_keys(self) -> None:
        engine = BattleEngine(seed=42, boss_id="earth")
        engine.begin_warning()
        data = state_to_dict(engine.state, engine.boss_id)
        self.assertEqual(data["bossId"], "earth")
        self.assertEqual(data["boardSize"], 7)
        self.assertEqual(len(data["party"]), 4)
        self.assertEqual(len(data["cells"]), 7)

    def test_end_phase_advances(self) -> None:
        engine = BattleEngine(seed=42, boss_id="earth")
        engine.begin_warning()
        self.assertEqual(engine.state.phase.name, "MOVE")
        engine.end_phase()
        self.assertEqual(engine.state.phase.name, "ACTION")


if __name__ == "__main__":
    unittest.main()
