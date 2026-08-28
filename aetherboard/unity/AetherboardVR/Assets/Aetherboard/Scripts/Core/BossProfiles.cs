using System;
using System.Collections.Generic;

namespace Aetherboard.Core
{
    public class TelegraphPreview
    {
        public TelegraphKind Telegraph;
        public string Message;
        public List<GridPos> DangerCells = new();
    }

    public interface IBossProfile
    {
        string BossId { get; }
        BossState Create();
        void UpdatePhase(BossState boss);
        TelegraphKind PickTelegraph(BossState boss, Random rng);
        TelegraphPreview Preview(TelegraphKind telegraph, int boardSize, BossState boss);
        (List<GridPos> hazards, List<string> logs) ResolveMechanic(
            TelegraphKind telegraph, BossState boss, int boardSize, Random rng);
        int MechanicDamage(TelegraphKind telegraph);
        int BasicDamage(BossState boss);
        string FuryName { get; }
        string VictoryMessage { get; }
        bool IsSpread(TelegraphKind t) => false;
        bool IsStack(TelegraphKind t) => false;
        bool IsIceRing(TelegraphKind t) => false;
        bool IsHeatLink(TelegraphKind t) => false;
    }

    public class EarthGuardianProfile : IBossProfile
    {
        public string BossId => "earth";

        public BossState Create() => new()
        {
            BossId = BossId,
            Name = "土灵守护者",
            Hp = 4200,
            MaxHp = 4200,
            Alive = true
        };

        public void UpdatePhase(BossState boss)
        {
            if (boss.HpRatio <= 0.4f) boss.Phase = 3;
            else if (boss.HpRatio <= 0.7f) boss.Phase = 2;
            else boss.Phase = 1;
        }

        public TelegraphKind PickTelegraph(BossState boss, Random rng)
        {
            if (boss.Phase == 1) return TelegraphKind.Slam;
            if (boss.Phase == 2) return TelegraphKind.Earthquake;
            if (boss.FuryCastTurns > 0) return TelegraphKind.EarthenFury;
            if (boss.ShrinkLevel < 1) return TelegraphKind.Shrink;
            return TelegraphKind.EarthenFury;
        }

        public TelegraphPreview Preview(TelegraphKind telegraph, int boardSize, BossState boss)
        {
            var preview = new TelegraphPreview { Telegraph = telegraph };
            preview.Message = telegraph switch
            {
                TelegraphKind.Slam => "Boss 预备重击：中心 3×3 将受重创。",
                TelegraphKind.Earthquake => "Boss 预备地震：随机 3×3 危险区。",
                TelegraphKind.Shrink => "Boss 预备缩圈：外圈变为即死区。",
                TelegraphKind.EarthenFury => "Boss 读条「土神之怒」：2 回合内必须打断！",
                _ => ""
            };
            if (telegraph == TelegraphKind.Slam)
                preview.DangerCells = BoardMath.PositionsInRadius(BoardMath.BoardCenter(boardSize), 1, boardSize);
            return preview;
        }

        public (List<GridPos>, List<string>) ResolveMechanic(
            TelegraphKind telegraph, BossState boss, int boardSize, Random rng)
        {
            var hazards = new List<GridPos>();
            var logs = new List<string>();
            switch (telegraph)
            {
                case TelegraphKind.Slam:
                    hazards = BoardMath.PositionsInRadius(BoardMath.BoardCenter(boardSize), 1, boardSize);
                    logs.Add("重击落下！");
                    break;
                case TelegraphKind.Earthquake:
                    var center = new GridPos(rng.Next(1, boardSize - 1), rng.Next(1, boardSize - 1));
                    hazards = BoardMath.PositionsInRadius(center, 1, boardSize);
                    logs.Add($"地震发生在 ({center.X}, {center.Y}) 附近！");
                    break;
                case TelegraphKind.Shrink:
                    boss.ShrinkLevel++;
                    hazards = BoardMath.RingPositions(boardSize, boss.ShrinkLevel);
                    logs.Add("外圈变为即死区！");
                    break;
                case TelegraphKind.EarthenFury when boss.FuryCastTurns > 0:
                    boss.FuryCastTurns--;
                    if (boss.FuryCastTurns == 0) logs.Add("土神之怒发动！");
                    break;
            }
            return (hazards, logs);
        }

        public int MechanicDamage(TelegraphKind telegraph) => telegraph switch
        {
            TelegraphKind.Slam => 180,
            TelegraphKind.Earthquake => 130,
            TelegraphKind.EarthenFury => 9999,
            _ => 0
        };

        public int BasicDamage(BossState boss) => boss.Phase switch
        {
            1 => 120,
            2 => 150,
            _ => 180
        };

        public string FuryName => "土神之怒";
        public string VictoryMessage => "胜利！土灵守护者被击败。";
    }

    public class WindSovereignProfile : IBossProfile
    {
        public string BossId => "wind";

        public BossState Create() => new()
        {
            BossId = BossId,
            Name = "风灵领主",
            Hp = 5000,
            MaxHp = 5000,
            Alive = true
        };

        public void UpdatePhase(BossState boss)
        {
            if (boss.HpRatio <= 0.4f) boss.Phase = 3;
            else if (boss.HpRatio <= 0.7f) boss.Phase = 2;
            else boss.Phase = 1;
        }

        public TelegraphKind PickTelegraph(BossState boss, Random rng)
        {
            if (boss.Phase == 1) return TelegraphKind.Gale;
            if (boss.Phase == 2) return TelegraphKind.Spread;
            if (boss.FuryCastTurns > 0) return TelegraphKind.Cyclone;
            return TelegraphKind.Stack;
        }

        public TelegraphPreview Preview(TelegraphKind telegraph, int boardSize, BossState boss)
        {
            var preview = new TelegraphPreview { Telegraph = telegraph };
            preview.Message = telegraph switch
            {
                TelegraphKind.Gale => "Boss 预备风刃：Boss 前方直线高伤。",
                TelegraphKind.Spread => "Boss 预备分散：相邻友军将受重罚。",
                TelegraphKind.Stack => "Boss 预备集合：必须靠近棋盘中心。",
                TelegraphKind.Cyclone => "Boss 读条「旋风」：2 回合内必须打断！",
                _ => ""
            };
            if (telegraph == TelegraphKind.Gale)
            {
                var cx = boardSize / 2;
                for (var y = 3; y < boardSize; y++) preview.DangerCells.Add(new GridPos(cx, y));
            }
            if (telegraph == TelegraphKind.Stack)
                preview.DangerCells = BoardMath.PositionsInRadius(BoardMath.BoardCenter(boardSize), 1, boardSize);
            return preview;
        }

        public (List<GridPos>, List<string>) ResolveMechanic(
            TelegraphKind telegraph, BossState boss, int boardSize, Random rng)
        {
            var hazards = new List<GridPos>();
            var logs = new List<string>();
            switch (telegraph)
            {
                case TelegraphKind.Gale:
                    var cx = boardSize / 2;
                    for (var y = 3; y < boardSize; y++) hazards.Add(new GridPos(cx, y));
                    logs.Add("风刃扫过中央列！");
                    break;
                case TelegraphKind.Spread:
                    logs.Add("分散判定：相邻友军受创！");
                    break;
                case TelegraphKind.Stack:
                    logs.Add("集合判定：远离中心者受创！");
                    break;
                case TelegraphKind.Cyclone when boss.FuryCastTurns > 0:
                    boss.FuryCastTurns--;
                    if (boss.FuryCastTurns == 0) logs.Add("旋风发动！");
                    break;
            }
            return (hazards, logs);
        }

        public int MechanicDamage(TelegraphKind telegraph) => telegraph switch
        {
            TelegraphKind.Gale => 150,
            TelegraphKind.Spread => 200,
            TelegraphKind.Stack => 220,
            TelegraphKind.Cyclone => 9999,
            _ => 0
        };

        public int BasicDamage(BossState boss) => boss.Phase switch
        {
            1 => 100,
            2 => 130,
            _ => 160
        };

        public string FuryName => "旋风";
        public string VictoryMessage => "胜利！风灵领主被击败。";
        public bool IsSpread(TelegraphKind t) => t == TelegraphKind.Spread;
        public bool IsStack(TelegraphKind t) => t == TelegraphKind.Stack;
    }

    public class IceEmpressProfile : IBossProfile
    {
        public string BossId => "ice";

        public BossState Create() => new()
        {
            BossId = BossId,
            Name = "冰灵女皇",
            Hp = 4800,
            MaxHp = 4800,
            Alive = true
        };

        public void UpdatePhase(BossState boss)
        {
            if (boss.HpRatio <= 0.4f) boss.Phase = 3;
            else if (boss.HpRatio <= 0.7f) boss.Phase = 2;
            else boss.Phase = 1;
        }

        public TelegraphKind PickTelegraph(BossState boss, Random rng)
        {
            if (boss.Phase == 1) return TelegraphKind.IceLance;
            if (boss.Phase == 2) return TelegraphKind.FrozenGround;
            if (boss.FuryCastTurns > 0) return TelegraphKind.Blizzard;
            if (boss.ShrinkLevel < 1) return TelegraphKind.IceRing;
            return TelegraphKind.Blizzard;
        }

        public TelegraphPreview Preview(TelegraphKind telegraph, int boardSize, BossState boss)
        {
            var preview = new TelegraphPreview { Telegraph = telegraph };
            preview.Message = telegraph switch
            {
                TelegraphKind.IceLance => "Boss 预备冰枪：十字路径高伤。",
                TelegraphKind.FrozenGround => "Boss 预备霜冻：2×2 危险区。",
                TelegraphKind.IceRing => "Boss 预备冰环：必须站在距离中心 2 格的环上。",
                TelegraphKind.Blizzard => "Boss 读条「暴雪」：2 回合内必须打断！",
                _ => ""
            };

            var bossPos = BoardMath.BossPos(boardSize);
            var center = BoardMath.BoardCenter(boardSize);
            if (telegraph == TelegraphKind.IceLance)
            {
                for (var x = 0; x < boardSize; x++) preview.DangerCells.Add(new GridPos(x, bossPos.Y));
                for (var y = 0; y < boardSize; y++)
                {
                    var p = new GridPos(bossPos.X, y);
                    if (!preview.DangerCells.Contains(p)) preview.DangerCells.Add(p);
                }
            }
            else if (telegraph == TelegraphKind.IceRing)
            {
                var ring = new HashSet<GridPos>(BoardMath.PositionsAtDistance(center, 2, boardSize));
                for (var x = 0; x < boardSize; x++)
                for (var y = 0; y < boardSize; y++)
                {
                    var p = new GridPos(x, y);
                    if (!ring.Contains(p)) preview.DangerCells.Add(p);
                }
            }
            return preview;
        }

        public (List<GridPos>, List<string>) ResolveMechanic(
            TelegraphKind telegraph, BossState boss, int boardSize, Random rng)
        {
            var hazards = new List<GridPos>();
            var logs = new List<string>();
            var bossPos = BoardMath.BossPos(boardSize);
            switch (telegraph)
            {
                case TelegraphKind.IceLance:
                    for (var x = 0; x < boardSize; x++) hazards.Add(new GridPos(x, bossPos.Y));
                    for (var y = 0; y < boardSize; y++)
                    {
                        var p = new GridPos(bossPos.X, y);
                        if (!hazards.Contains(p)) hazards.Add(p);
                    }
                    logs.Add("冰枪十字扫过棋盘！");
                    break;
                case TelegraphKind.FrozenGround:
                    logs.Add("霜冻区域爆发！");
                    break;
                case TelegraphKind.IceRing:
                    boss.ShrinkLevel += 1;
                    logs.Add("冰环收缩：未站在环上者受创！");
                    break;
                case TelegraphKind.Blizzard when boss.FuryCastTurns > 0:
                    boss.FuryCastTurns -= 1;
                    if (boss.FuryCastTurns == 0) logs.Add("暴雪发动！");
                    break;
            }
            return (hazards, logs);
        }

        public int MechanicDamage(TelegraphKind telegraph) => telegraph switch
        {
            TelegraphKind.IceLance => 160,
            TelegraphKind.FrozenGround => 140,
            TelegraphKind.IceRing => 210,
            TelegraphKind.Blizzard => 9999,
            _ => 0
        };

        public int BasicDamage(BossState boss) => boss.Phase switch
        {
            1 => 110,
            2 => 140,
            _ => 170
        };

        public string FuryName => "暴雪";
        public string VictoryMessage => "胜利！冰灵女皇被击败。";
        public bool IsIceRing(TelegraphKind t) => t == TelegraphKind.IceRing;
    }

    public class FireSovereignProfile : IBossProfile
    {
        public string BossId => "fire";

        public BossState Create() => new()
        {
            BossId = BossId,
            Name = "火灵君主",
            Hp = 5200,
            MaxHp = 5200,
            Alive = true
        };

        public void UpdatePhase(BossState boss)
        {
            if (boss.HpRatio <= 0.4f) boss.Phase = 3;
            else if (boss.HpRatio <= 0.7f) boss.Phase = 2;
            else boss.Phase = 1;
        }

        public TelegraphKind PickTelegraph(BossState boss, Random rng)
        {
            if (boss.Phase == 1) return TelegraphKind.FlameBreath;
            if (boss.Phase == 2) return TelegraphKind.Meteor;
            if (boss.FuryCastTurns > 0) return TelegraphKind.Eruption;
            if (boss.ShrinkLevel < 1) return TelegraphKind.HeatLink;
            return TelegraphKind.Eruption;
        }

        public TelegraphPreview Preview(TelegraphKind telegraph, int boardSize, BossState boss)
        {
            var preview = new TelegraphPreview { Telegraph = telegraph };
            preview.Message = telegraph switch
            {
                TelegraphKind.FlameBreath => "Boss 预备火息：对角线 X 路径高伤。",
                TelegraphKind.Meteor => "Boss 预备陨石：随机落点危险区。",
                TelegraphKind.HeatLink => "Boss 预备灼热连结：必须与友军相邻。",
                TelegraphKind.Eruption => "Boss 读条「喷发」：2 回合内必须打断！",
                _ => ""
            };
            if (telegraph == TelegraphKind.FlameBreath)
                preview.DangerCells = BoardMath.PositionsDiagonals(BoardMath.BoardCenter(boardSize), boardSize);
            return preview;
        }

        public (List<GridPos>, List<string>) ResolveMechanic(
            TelegraphKind telegraph, BossState boss, int boardSize, Random rng)
        {
            var hazards = new List<GridPos>();
            var logs = new List<string>();
            switch (telegraph)
            {
                case TelegraphKind.FlameBreath:
                    hazards = BoardMath.PositionsDiagonals(BoardMath.BoardCenter(boardSize), boardSize);
                    logs.Add("火息沿对角线扫过！");
                    break;
                case TelegraphKind.Meteor:
                    logs.Add("陨石砸落！");
                    break;
                case TelegraphKind.HeatLink:
                    boss.ShrinkLevel += 1;
                    logs.Add("灼热连结：孤身者受创！");
                    break;
                case TelegraphKind.Eruption when boss.FuryCastTurns > 0:
                    boss.FuryCastTurns -= 1;
                    if (boss.FuryCastTurns == 0) logs.Add("喷发发动！");
                    break;
            }
            return (hazards, logs);
        }

        public int MechanicDamage(TelegraphKind telegraph) => telegraph switch
        {
            TelegraphKind.FlameBreath => 155,
            TelegraphKind.Meteor => 150,
            TelegraphKind.HeatLink => 200,
            TelegraphKind.Eruption => 9999,
            _ => 0
        };

        public int BasicDamage(BossState boss) => boss.Phase switch
        {
            1 => 115,
            2 => 145,
            _ => 175
        };

        public string FuryName => "喷发";
        public string VictoryMessage => "胜利！火灵君主被击败。";
        public bool IsHeatLink(TelegraphKind t) => t == TelegraphKind.HeatLink;
    }

    public static class BossRegistry
    {
        private static readonly Dictionary<string, IBossProfile> Profiles = new()
        {
            ["earth"] = new EarthGuardianProfile(),
            ["wind"] = new WindSovereignProfile(),
            ["ice"] = new IceEmpressProfile(),
            ["fire"] = new FireSovereignProfile(),
        };

        public static IBossProfile Get(string bossId) =>
            Profiles.TryGetValue(bossId, out var p) ? p : Profiles["earth"];

        public static IReadOnlyList<string> AllBossIds { get; } =
            new List<string>(Profiles.Keys);

        public static string DisplayName(string bossId) => Get(bossId).Create().Name;

        public static readonly IReadOnlyList<string> BossOrder = new List<string>
        {
            "earth", "wind", "ice", "fire"
        };

        public static string MechanicSummary(string bossId) => bossId switch
        {
            "wind" => "P1 风刃 · P2 分散 · P3 集合+旋风",
            "ice" => "P1 冰枪 · P2 霜冻 · P3 冰环+暴雪",
            "fire" => "P1 火息 · P2 陨石 · P3 连结+喷发",
            _ => "P1 重击 · P2 地震 · P3 缩圈+土神之怒"
        };

        public static string CycleBossId(string currentId)
        {
            var order = BossOrder;
            var idx = 0;
            for (var i = 0; i < order.Count; i++)
            {
                if (order[i] == currentId)
                {
                    idx = i;
                    break;
                }
            }
            return order[(idx + 1) % order.Count];
        }
    }
}
