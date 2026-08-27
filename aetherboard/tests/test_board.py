"""Tests for board helpers."""

import unittest

from sim.board import apply_shrink, is_deadly, make_board, ring_positions
from sim.types import CellKind, Pos


class BoardTests(unittest.TestCase):
    def test_shrink_marks_outer_ring(self) -> None:
        cells = make_board()
        apply_shrink(cells, 7, 1)
        self.assertTrue(is_deadly(cells, Pos(0, 0)))
        self.assertFalse(is_deadly(cells, Pos(3, 3)))

    def test_ring_positions_depth(self) -> None:
        ring = ring_positions(7, 1)
        self.assertIn(Pos(0, 3), ring)
        self.assertNotIn(Pos(3, 3), ring)


if __name__ == "__main__":
    unittest.main()
