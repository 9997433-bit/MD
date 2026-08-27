"""Split-coop unit ownership rules."""

from __future__ import annotations

PLAYER1_UNITS = frozenset({"knight", "bard"})
PLAYER2_UNITS = frozenset({"white_mage", "black_mage"})


def can_control(player_id: int, unit_id: str, coop_enabled: bool) -> bool:
    if not coop_enabled or player_id <= 0 or not unit_id:
        return True
    allowed = PLAYER1_UNITS if player_id == 1 else PLAYER2_UNITS
    return unit_id in allowed


def command_requires_unit(cmd_type: str) -> bool:
    return cmd_type in {"Move", "Skill"}
