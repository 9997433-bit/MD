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

    public static class BossRegistry
    {
        private static readonly Dictionary<string, IBossProfile> Profiles = new()
        {
            ["earth"] = new EarthGuardianProfile(),
            ["wind"] = new WindSovereignProfile(),
        };

        public static IBossProfile Get(string bossId) =>
            Profiles.TryGetValue(bossId, out var p) ? p : Profiles["earth"];

        public static IReadOnlyList<string> AllBossIds { get; } =
            new List<string>(Profiles.Keys);

        public static string DisplayName(string bossId) => Get(bossId).Create().Name;
    }
}
