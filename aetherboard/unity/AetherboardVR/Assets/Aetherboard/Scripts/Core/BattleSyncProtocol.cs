using System.Text;

namespace Aetherboard.Core
{
    /// <summary>
    /// Line-delimited JSON envelopes for host/client sync (TCP or WebSocket).
    /// </summary>
    public static class BattleSyncProtocol
    {
        public const string TypeWelcome = "welcome";
        public const string TypeState = "state";
        public const string TypeCommand = "command";
        public const string TypeError = "error";

        public static string EncodeWelcome(int seed, string bossId, bool coop = false) =>
            $"{{\"type\":\"{TypeWelcome}\",\"seed\":{seed},\"bossId\":\"{bossId}\",\"coop\":{(coop ? "true" : "false")}}}";

        public static string EncodeState(string stateJson) =>
            $"{{\"type\":\"{TypeState}\",\"payload\":{stateJson}}}";

        public static string EncodeCommand(BattleCommand cmd)
        {
            var sb = new StringBuilder(256);
            sb.Append("{\"type\":\"").Append(TypeCommand).Append("\",\"cmd\":{");
            sb.Append("\"type\":\"").Append(cmd.Type).Append("\",");
            sb.Append("\"unitId\":\"").Append(cmd.UnitId ?? "").Append("\",");
            sb.Append("\"skillId\":\"").Append(cmd.SkillId ?? "").Append("\",");
            sb.Append("\"targetX\":").Append(cmd.TargetX).Append(',');
            sb.Append("\"targetY\":").Append(cmd.TargetY).Append(',');
            sb.Append("\"bossId\":\"").Append(cmd.BossId ?? "").Append("\",");
            sb.Append("\"playerId\":").Append(cmd.PlayerId);
            sb.Append("}}");
            return sb.ToString();
        }

        public static string EncodeError(string message) =>
            $"{{\"type\":\"{TypeError}\",\"message\":\"{Escape(message)}\"}}";

        public static string ExtractType(string line)
        {
            var root = SimpleJson.ParseObject(line);
            return root.GetString("type");
        }

        public static string ExtractStatePayload(string line)
        {
            var root = SimpleJson.ParseObject(line);
            var payload = root.GetObject("payload");
            if (payload == null) return null;
            return ReSerializeObject(payload);
        }

        public static BattleCommand ExtractCommand(string line)
        {
            var root = SimpleJson.ParseObject(line);
            var cmd = root.GetObject("cmd");
            if (cmd == null) return null;
            var typeStr = cmd.GetString("type");
            if (!System.Enum.TryParse<BattleCommandType>(typeStr, out var type))
                return null;
            return new BattleCommand
            {
                Type = type,
                UnitId = cmd.GetString("unitId"),
                SkillId = cmd.GetString("skillId"),
                TargetX = cmd.GetInt("targetX", -1),
                TargetY = cmd.GetInt("targetY", -1),
                BossId = cmd.GetString("bossId"),
                PlayerId = cmd.GetInt("playerId")
            };
        }

        private static string ReSerializeObject(System.Collections.Generic.Dictionary<string, object> obj)
        {
            var sb = new StringBuilder(512);
            sb.Append('{');
            var first = true;
            foreach (var kv in obj)
            {
                if (!first) sb.Append(',');
                first = false;
                sb.Append('"').Append(kv.Key).Append("\":");
                sb.Append(ValueToJson(kv.Value));
            }
            sb.Append('}');
            return sb.ToString();
        }

        private static string ValueToJson(object value)
        {
            switch (value)
            {
                case string s: return $"\"{Escape(s)}\"";
                case bool b: return b ? "true" : "false";
                case double d: return d.ToString(System.Globalization.CultureInfo.InvariantCulture);
                case System.Collections.Generic.Dictionary<string, object> dict:
                    return ReSerializeObject(dict);
                case System.Collections.Generic.List<object> list:
                {
                    var sb = new StringBuilder();
                    sb.Append('[');
                    for (var i = 0; i < list.Count; i++)
                    {
                        if (i > 0) sb.Append(',');
                        sb.Append(ValueToJson(list[i]));
                    }
                    sb.Append(']');
                    return sb.ToString();
                }
                default: return "null";
            }
        }

        private static string Escape(string s) =>
            (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"");
    }
}
