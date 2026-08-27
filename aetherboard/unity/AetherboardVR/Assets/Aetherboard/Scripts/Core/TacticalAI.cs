using System;
using System.Collections.Generic;
using System.Linq;

namespace Aetherboard.Core
{
    public static class TacticalAI
    {
        private static int EdgePenalty(GridPos pos, int size)
        {
            var s = 0;
            if (pos.X <= 0 || pos.X >= size - 1 || pos.Y <= 0 || pos.Y >= size - 1) s -= 40;
            else if (pos.X <= 1 || pos.X >= size - 2 || pos.Y <= 1 || pos.Y >= size - 2) s -= 15;
            return s;
        }

        private static int MinDist(UnitState unit, GridPos pos, List<UnitState> party)
        {
            var others = party.Where(u => u.Alive && u.Id != unit.Id).ToList();
            if (others.Count == 0) return 99;
            return others.Min(u => u.Pos.Distance(pos));
        }

        public static int ScorePosition(UnitState unit, GridPos pos, BattleState state)
        {
            var telegraph = state.Boss.Telegraph;
            var center = BoardMath.BoardCenter(state.BoardSize);
            var boss = BoardMath.BossPos(state.BoardSize);
            var score = EdgePenalty(pos, state.BoardSize);
            var party = state.Party.Where(u => u.Alive).ToList();

            switch (telegraph)
            {
                case TelegraphKind.Slam:
                    score += pos.Distance(center) * 3;
                    break;
                case TelegraphKind.Earthquake:
                    if (state.PendingHazards.Any(p => p.Equals(pos))) score -= 80;
                    score += pos.Distance(center) * 2;
                    break;
                case TelegraphKind.Shrink:
                    score += pos.Distance(center) * 4;
                    if (pos.Y >= state.BoardSize - 2) score -= 25;
                    break;
                case TelegraphKind.Spread:
                    score += MinDist(unit, pos, party) * 5;
                    break;
                case TelegraphKind.Stack:
                    score -= pos.Distance(center) * 4;
                    break;
                case TelegraphKind.Gale:
                    if (pos.X == boss.X) score -= 10;
                    score += pos.Distance(boss) * 2;
                    break;
                default:
                    score += MinDist(unit, pos, party);
                    break;
            }

            if (unit.Job == JobType.BlackMage && !pos.Equals(unit.Pos)) score -= 2;
            if (unit.Job == JobType.Knight && telegraph != TelegraphKind.Spread)
                score -= pos.Distance(boss) * 2;
            if (BoardMath.IsDeadly(state.Cells, pos)) score -= 1000;
            return score;
        }

        public static GridPos PickMoveDest(UnitState unit, BattleState state)
        {
            var occupied = new HashSet<(int, int)>(
                state.Party.Where(u => u.Alive && u.Id != unit.Id).Select(u => (u.Pos.X, u.Pos.Y)));
            var options = new List<GridPos>();
            var range = JobCatalog.MoveRange[unit.Job];
            for (var x = 0; x < state.BoardSize; x++)
            for (var y = 0; y < state.BoardSize; y++)
            {
                var dest = new GridPos(x, y);
                if (!dest.InBounds(state.BoardSize)) continue;
                if (BoardMath.IsDeadly(state.Cells, dest)) continue;
                if (dest.Equals(BoardMath.BossPos(state.BoardSize))) continue;
                if (occupied.Contains((x, y)) && !dest.Equals(unit.Pos)) continue;
                if (unit.Pos.Distance(dest) <= range) options.Add(dest);
            }
            if (options.Count == 0) return unit.Pos;
            return options.OrderByDescending(p => ScorePosition(unit, p, state)).First();
        }

        public static string PickGcdSkill(UnitState unit, BattleState state)
        {
            if (unit.Job == JobType.WhiteMage)
            {
                var low = state.Party.Where(u => u.Alive).Min(u => (float)u.Hp / u.MaxHp);
                return low < 0.45f ? "medica" : "cure";
            }
            if (unit.Job == JobType.BlackMage && !unit.MovedThisTurn) return "fire";
            return JobCatalog.JobSkills[unit.Job][0];
        }

        public static GridPos PickGcdTarget(UnitState unit, BattleState state)
        {
            if (unit.Job == JobType.WhiteMage)
                return state.Party.Where(u => u.Alive).OrderBy(u => (float)u.Hp / u.MaxHp).First().Pos;
            return BoardMath.BossPos(state.BoardSize);
        }

        public static (string skillId, GridPos? target)? PickOgcd(UnitState unit, BattleState state)
        {
            if (state.Boss.FuryCastTurns > 0)
                return ("interrupt", BoardMath.BossPos(state.BoardSize));
            if (unit.Job == JobType.Knight && unit.MitTurns == 0 && state.Boss.Phase >= 2)
                return ("rampart", unit.Pos);
            if (unit.Job == JobType.WhiteMage)
            {
                var low = state.Party.Where(u => u.Alive).OrderBy(u => (float)u.Hp / u.MaxHp).First();
                if ((float)low.Hp / low.MaxHp < 0.35f) return ("benediction", low.Pos);
            }
            if (unit.Job == JobType.BlackMage && unit.MitTurns == 0) return ("manaward", unit.Pos);
            if (unit.Job == JobType.Bard && !state.Party.Any(u => u.Alive && u.BardSongTurns > 0))
                return ("mages_ballad", unit.Pos);
            if (unit.Job == JobType.Knight && state.Boss.Phase >= 2)
                return ("provoke", BoardMath.BossPos(state.BoardSize));
            return null;
        }
    }
}
