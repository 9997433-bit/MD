using System;
using System.Collections.Generic;
using System.Text;

namespace Aetherboard.Core
{
    public enum BattleCommandType
    {
        Move,
        Skill,
        EndPhase,
        SetBoss
    }

    [Serializable]
    public class BattleCommand
    {
        public int Turn;
        public BattlePhase Phase;
        public BattleCommandType Type;
        public string UnitId;
        public string SkillId;
        public int TargetX = -1;
        public int TargetY = -1;
        public string BossId;
        public int PlayerId;
    }

    /// <summary>
    /// Records player-issued commands for replay and future host-authoritative sync.
    /// </summary>
    public class BattleCommandLog
    {
        public int RandomSeed { get; set; }
        public string BossId { get; set; } = "earth";
        public List<BattleCommand> Commands { get; } = new();

        public void Record(BattleCommand cmd) => Commands.Add(cmd);

        public string ToJson()
        {
            var sb = new StringBuilder(512);
            sb.Append("{\"seed\":").Append(RandomSeed)
                .Append(",\"bossId\":\"").Append(BossId).Append("\",\"commands\":[");
            for (var i = 0; i < Commands.Count; i++)
            {
                if (i > 0) sb.Append(',');
                AppendCommandJson(sb, Commands[i]);
            }
            sb.Append("]}");
            return sb.ToString();
        }

        public static BattleCommandLog FromJson(string json)
        {
            var root = SimpleJson.ParseObject(json);
            var log = new BattleCommandLog
            {
                RandomSeed = root.GetInt("seed", 42),
                BossId = root.GetString("bossId") ?? "earth"
            };
            var commands = root.GetArray("commands");
            if (commands == null) return log;

            foreach (var item in commands)
            {
                if (item is not Dictionary<string, object> obj) continue;
                log.Commands.Add(ParseCommand(obj));
            }
            return log;
        }

        private static void AppendCommandJson(StringBuilder sb, BattleCommand c)
        {
            sb.Append('{')
                .Append("\"turn\":").Append(c.Turn).Append(',')
                .Append("\"phase\":\"").Append(c.Phase).Append("\",")
                .Append("\"type\":\"").Append(c.Type).Append("\",")
                .Append("\"unitId\":\"").Append(c.UnitId ?? "").Append("\",")
                .Append("\"skillId\":\"").Append(c.SkillId ?? "").Append("\",")
                .Append("\"targetX\":").Append(c.TargetX).Append(',')
                .Append("\"targetY\":").Append(c.TargetY).Append(',')
                .Append("\"bossId\":\"").Append(c.BossId ?? "").Append("\"")
                .Append('}');
        }

        private static BattleCommand ParseCommand(Dictionary<string, object> obj) => new()
        {
            Turn = obj.GetInt("turn"),
            Phase = Enum.TryParse<BattlePhase>(obj.GetString("phase"), out var phase)
                ? phase
                : BattlePhase.Warning,
            Type = Enum.TryParse<BattleCommandType>(obj.GetString("type"), out var type)
                ? type
                : BattleCommandType.EndPhase,
            UnitId = obj.GetString("unitId"),
            SkillId = obj.GetString("skillId"),
            TargetX = obj.GetInt("targetX", -1),
            TargetY = obj.GetInt("targetY", -1),
            BossId = obj.GetString("bossId"),
            PlayerId = obj.GetInt("playerId")
        };
    }
}
