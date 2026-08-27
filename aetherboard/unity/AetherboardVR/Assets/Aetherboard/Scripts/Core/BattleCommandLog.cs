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
                var c = Commands[i];
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
            sb.Append("]}");
            return sb.ToString();
        }
    }
}
