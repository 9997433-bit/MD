using System.Collections.Generic;

namespace Aetherboard.Core
{
    public static class BoardMath
    {
        public const int DefaultSize = 7;

        public static GridPos BossPos(int size) => new(size / 2, 2);
        public static GridPos BoardCenter(int size) => new(size / 2, size / 2);

        public static CellKind[,] MakeBoard(int size = DefaultSize)
        {
            var cells = new CellKind[size, size];
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
                cells[y, x] = CellKind.Normal;
            return cells;
        }

        public static List<GridPos> PositionsInRadius(GridPos center, int radius, int size)
        {
            var list = new List<GridPos>();
            for (var x = 0; x < size; x++)
            for (var y = 0; y < size; y++)
            {
                var p = new GridPos(x, y);
                if (p.Distance(center) <= radius) list.Add(p);
            }
            return list;
        }

        public static List<GridPos> PositionsAtDistance(GridPos center, int distance, int size)
        {
            var list = new List<GridPos>();
            for (var x = 0; x < size; x++)
            for (var y = 0; y < size; y++)
            {
                var p = new GridPos(x, y);
                if (p.Distance(center) == distance) list.Add(p);
            }
            return list;
        }

        public static List<GridPos> Positions2x2(GridPos topLeft, int size)
        {
            var list = new List<GridPos>();
            for (var dx = 0; dx < 2; dx++)
            for (var dy = 0; dy < 2; dy++)
            {
                var p = new GridPos(topLeft.X + dx, topLeft.Y + dy);
                if (p.InBounds(size)) list.Add(p);
            }
            return list;
        }

        public static List<GridPos> RingPositions(int size, int shrinkLevel)
        {
            var list = new List<GridPos>();
            if (shrinkLevel <= 0) return list;
            var depth = shrinkLevel - 1;
            for (var x = 0; x < size; x++)
            for (var y = 0; y < size; y++)
            {
                if (x <= depth || y <= depth || x >= size - 1 - depth || y >= size - 1 - depth)
                    list.Add(new GridPos(x, y));
            }
            return list;
        }

        public static bool IsDeadly(CellKind[,] cells, GridPos pos) =>
            cells[pos.Y, pos.X] == CellKind.Hazard;

        public static void ClearHazards(CellKind[,] cells, int size)
        {
            for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
                if (cells[y, x] == CellKind.Hazard)
                    cells[y, x] = CellKind.Normal;
        }

        public static void ApplyHazards(CellKind[,] cells, IEnumerable<GridPos> hazards)
        {
            foreach (var p in hazards)
                cells[p.Y, p.X] = CellKind.Hazard;
        }
    }
}
