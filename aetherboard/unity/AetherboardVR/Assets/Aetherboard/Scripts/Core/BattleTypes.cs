using System;
using System.Collections.Generic;

namespace Aetherboard.Core
{
    public enum BattlePhase
    {
        Warning,
        Move,
        Action,
        Weave,
        Resolve,
        Victory,
        Defeat
    }

    public enum JobType
    {
        Knight,
        WhiteMage,
        BlackMage,
        Bard
    }

    public enum CellKind
    {
        Normal,
        Hazard,
        Safe
    }

    public enum TelegraphKind
    {
        None,
        Slam,
        Earthquake,
        Shrink,
        EarthenFury,
        Gale,
        Spread,
        Stack,
        Cyclone,
        IceLance,
        FrozenGround,
        IceRing,
        Blizzard,
        FlameBreath,
        Meteor,
        HeatLink,
        Eruption
    }

    [Serializable]
    public struct GridPos : IEquatable<GridPos>
    {
        public int X;
        public int Y;

        public GridPos(int x, int y)
        {
            X = x;
            Y = y;
        }

        public int Distance(GridPos other) =>
            Math.Abs(X - other.X) + Math.Abs(Y - other.Y);

        public bool InBounds(int size) =>
            X >= 0 && Y >= 0 && X < size && Y < size;

        public bool Equals(GridPos other) => X == other.X && Y == other.Y;
        public override bool Equals(object obj) => obj is GridPos p && Equals(p);
        public override int GetHashCode() => HashCode.Combine(X, Y);
        public override string ToString() => $"({X},{Y})";
    }

    [Serializable]
    public class SkillDef
    {
        public string Id;
        public string Name;
        public string Kind;
        public int Range;
        public int Power;
        public int Heal;
        public int AoeRadius;
        public int MitDuration;
    }

    [Serializable]
    public class UnitState
    {
        public string Id;
        public string DisplayName;
        public JobType Job;
        public GridPos Pos;
        public int Hp;
        public int MaxHp;
        public bool Alive = true;
        public bool MovedThisTurn;
        public bool GcdUsed;
        public bool OgcdUsed;
        public int MitTurns;
        public int BardSongTurns;
        public int TauntTurns;

        public void ResetTurnFlags()
        {
            MovedThisTurn = false;
            GcdUsed = false;
            OgcdUsed = false;
        }
    }

    [Serializable]
    public class BossState
    {
        public string Name;
        public string BossId;
        public int Hp;
        public int MaxHp;
        public int Phase = 1;
        public TelegraphKind Telegraph = TelegraphKind.None;
        public int FuryCastTurns;
        public int ShrinkLevel;
        public bool Alive = true;

        public float HpRatio => MaxHp > 0 ? (float)Hp / MaxHp : 0f;
    }

    [Serializable]
    public class BattleState
    {
        public int Turn = 1;
        public BattlePhase Phase = BattlePhase.Warning;
        public int BoardSize = 7;
        public CellKind[,] Cells;
        public List<UnitState> Party = new();
        public BossState Boss = new();
        public List<string> Log = new();
        public List<GridPos> PendingHazards = new();
        public List<GridPos> PreviewCells = new();
    }
}
