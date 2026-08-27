"""7x7 board helpers."""

from __future__ import annotations

from .types import CellKind, Pos


def make_board(size: int = 7) -> list[list[CellKind]]:
    return [[CellKind.NORMAL for _ in range(size)] for _ in range(size)]


def in_bounds(pos: Pos, size: int) -> bool:
    return pos.in_bounds(size)


def neighbors(pos: Pos, size: int) -> list[Pos]:
    result: list[Pos] = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        candidate = Pos(pos.x + dx, pos.y + dy)
        if candidate.in_bounds(size):
            result.append(candidate)
    return result


def ring_positions(size: int, shrink_level: int) -> list[Pos]:
    """Outer ring at a given shrink depth becomes deadly."""
    if shrink_level <= 0:
        return []
    depth = shrink_level - 1
    positions: list[Pos] = []
    for x in range(size):
        for y in range(size):
            if (
                x <= depth
                or y <= depth
                or x >= size - 1 - depth
                or y >= size - 1 - depth
            ):
                positions.append(Pos(x, y))
    return positions


def apply_hazards(
    cells: list[list[CellKind]], hazards: list[Pos], size: int
) -> None:
    for pos in hazards:
        if pos.in_bounds(size):
            cells[pos.y][pos.x] = CellKind.HAZARD


def clear_hazards(cells: list[list[CellKind]], size: int) -> None:
    for y in range(size):
        for x in range(size):
            if cells[y][x] == CellKind.HAZARD:
                cells[y][x] = CellKind.NORMAL


def apply_shrink(
    cells: list[list[CellKind]], size: int, shrink_level: int
) -> None:
    for pos in ring_positions(size, shrink_level):
        cells[pos.y][pos.x] = CellKind.HAZARD


def is_deadly(cells: list[list[CellKind]], pos: Pos) -> bool:
    return cells[pos.y][pos.x] == CellKind.HAZARD


def positions_in_radius(center: Pos, radius: int, size: int) -> list[Pos]:
    positions: list[Pos] = []
    for x in range(size):
        for y in range(size):
            candidate = Pos(x, y)
            if candidate.distance(center) <= radius:
                positions.append(candidate)
    return positions
