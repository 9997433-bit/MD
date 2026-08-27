using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Aetherboard.Core
{
    /// <summary>
    /// JSON codec aligned with schema/battle_state.schema.json — foundation for replay and network sync.
    /// </summary>
    public static class BattleStateCodec
    {
        public static string Serialize(BattleState state, string bossId)
        {
            var sb = new StringBuilder(2048);
            sb.Append('{');
            AppendPair(sb, "turn", state.Turn);
            AppendPair(sb, "phase", PhaseToSchema(state.Phase), true);
            AppendPair(sb, "boardSize", state.BoardSize);
            AppendPair(sb, "bossId", bossId, true);
            AppendBoss(sb, state.Boss);
            AppendParty(sb, state.Party);
            AppendCells(sb, state.Cells, state.BoardSize);
            AppendPositions(sb, "pendingHazards", state.PendingHazards);
            AppendPositions(sb, "previewCells", state.PreviewCells);
            AppendLog(sb, state.Log);
            sb.Append('}');
            return sb.ToString();
        }

        public static (BattleState state, string bossId) Deserialize(string json)
        {
            var root = SimpleJson.ParseObject(json);
            var bossId = root.GetString("bossId") ?? "earth";
            var size = root.GetInt("boardSize", BoardMath.DefaultSize);
            var state = new BattleState
            {
                Turn = root.GetInt("turn", 1),
                Phase = PhaseFromSchema(root.GetString("phase")),
                BoardSize = size,
                Boss = ParseBoss(root.GetObject("boss")),
                Party = ParseParty(root.GetArray("party")),
                Cells = ParseCells(root.GetArray("cells"), size),
                PendingHazards = ParsePositions(root.GetArray("pendingHazards")),
                PreviewCells = ParsePositions(root.GetArray("previewCells")),
                Log = ParseLog(root.GetArray("log"))
            };
            return (state, bossId);
        }

        public static BattleState Clone(BattleState source)
        {
            var json = Serialize(source, source.Boss.BossId);
            var (clone, _) = Deserialize(json);
            return clone;
        }

        private static void AppendBoss(StringBuilder sb, BossState boss)
        {
            sb.Append("\"boss\":{");
            AppendPair(sb, "name", boss.Name, true);
            AppendPair(sb, "hp", boss.Hp);
            AppendPair(sb, "maxHp", boss.MaxHp);
            AppendPair(sb, "phase", boss.Phase);
            AppendPair(sb, "telegraph", TelegraphToSchema(boss.Telegraph), true);
            AppendPair(sb, "furyCastTurns", boss.FuryCastTurns);
            AppendPair(sb, "shrinkLevel", boss.ShrinkLevel);
            AppendPair(sb, "alive", boss.Alive ? "true" : "false", true, false);
            sb.Append('}');
            sb.Append(',');
        }

        private static BossState ParseBoss(Dictionary<string, object> obj)
        {
            if (obj == null) return new BossState();
            return new BossState
            {
                Name = obj.GetString("name") ?? "",
                BossId = obj.GetString("bossId") ?? "",
                Hp = obj.GetInt("hp"),
                MaxHp = obj.GetInt("maxHp"),
                Phase = obj.GetInt("phase", 1),
                Telegraph = TelegraphFromSchema(obj.GetString("telegraph")),
                FuryCastTurns = obj.GetInt("furyCastTurns"),
                ShrinkLevel = obj.GetInt("shrinkLevel"),
                Alive = obj.GetBool("alive", true)
            };
        }

        private static void AppendParty(StringBuilder sb, List<UnitState> party)
        {
            sb.Append("\"party\":[");
            for (var i = 0; i < party.Count; i++)
            {
                var u = party[i];
                if (i > 0) sb.Append(',');
                sb.Append('{');
                AppendPair(sb, "id", u.Id, true);
                AppendPair(sb, "name", u.DisplayName, true);
                AppendPair(sb, "job", JobToSchema(u.Job), true);
                sb.Append("\"pos\":{\"x\":").Append(u.Pos.X).Append(",\"y\":").Append(u.Pos.Y).Append("},");
                AppendPair(sb, "hp", u.Hp);
                AppendPair(sb, "maxHp", u.MaxHp);
                AppendPair(sb, "alive", u.Alive ? "true" : "false", true);
                AppendPair(sb, "moved", u.MovedThisTurn ? "true" : "false", true);
                AppendPair(sb, "gcdUsed", u.GcdUsed ? "true" : "false", true);
                AppendPair(sb, "ogcdUsed", u.OgcdUsed ? "true" : "false", true);
                AppendPair(sb, "mitTurns", u.MitTurns);
                AppendPair(sb, "songTurns", u.BardSongTurns);
                AppendPair(sb, "tauntTurns", u.TauntTurns, false, false);
                sb.Append('}');
            }
            sb.Append("],");
        }

        private static List<UnitState> ParseParty(List<object> arr)
        {
            var list = new List<UnitState>();
            if (arr == null) return list;
            foreach (var item in arr)
            {
                if (item is not Dictionary<string, object> obj) continue;
                var pos = obj.GetObject("pos");
                list.Add(new UnitState
                {
                    Id = obj.GetString("id") ?? "",
                    DisplayName = obj.GetString("name") ?? "",
                    Job = JobFromSchema(obj.GetString("job")),
                    Pos = new GridPos(pos?.GetInt("x") ?? 0, pos?.GetInt("y") ?? 0),
                    Hp = obj.GetInt("hp"),
                    MaxHp = obj.GetInt("maxHp"),
                    Alive = obj.GetBool("alive", true),
                    MovedThisTurn = obj.GetBool("moved"),
                    GcdUsed = obj.GetBool("gcdUsed"),
                    OgcdUsed = obj.GetBool("ogcdUsed"),
                    MitTurns = obj.GetInt("mitTurns"),
                    BardSongTurns = obj.GetInt("songTurns"),
                    TauntTurns = obj.GetInt("tauntTurns")
                });
            }
            return list;
        }

        private static void AppendCells(StringBuilder sb, CellKind[,] cells, int size)
        {
            sb.Append("\"cells\":[");
            for (var y = 0; y < size; y++)
            {
                if (y > 0) sb.Append(',');
                sb.Append('[');
                for (var x = 0; x < size; x++)
                {
                    if (x > 0) sb.Append(',');
                    sb.Append('"').Append(CellToSchema(cells[y, x])).Append('"');
                }
                sb.Append(']');
            }
            sb.Append("],");
        }

        private static CellKind[,] ParseCells(List<object> rows, int size)
        {
            var cells = BoardMath.MakeBoard();
            if (rows == null) return cells;
            for (var y = 0; y < Math.Min(size, rows.Count); y++)
            {
                if (rows[y] is not List<object> row) continue;
                for (var x = 0; x < Math.Min(size, row.Count); x++)
                    cells[y, x] = CellFromSchema(row[x]?.ToString());
            }
            return cells;
        }

        private static void AppendPositions(StringBuilder sb, string key, List<GridPos> positions)
        {
            sb.Append('"').Append(key).Append("\":[");
            for (var i = 0; i < positions.Count; i++)
            {
                if (i > 0) sb.Append(',');
                var p = positions[i];
                sb.Append("{\"x\":").Append(p.X).Append(",\"y\":").Append(p.Y).Append('}');
            }
            sb.Append("],");
        }

        private static List<GridPos> ParsePositions(List<object> arr)
        {
            var list = new List<GridPos>();
            if (arr == null) return list;
            foreach (var item in arr)
            {
                if (item is not Dictionary<string, object> obj) continue;
                list.Add(new GridPos(obj.GetInt("x"), obj.GetInt("y")));
            }
            return list;
        }

        private static void AppendLog(StringBuilder sb, List<string> log)
        {
            sb.Append("\"log\":[");
            for (var i = 0; i < log.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('"').Append(Escape(log[i])).Append('"');
            }
            sb.Append(']');
        }

        private static List<string> ParseLog(List<object> arr)
        {
            var list = new List<string>();
            if (arr == null) return list;
            foreach (var item in arr)
                if (item is string s) list.Add(s);
            return list;
        }

        private static void AppendPair(
            StringBuilder sb, string key, object value, bool quoted = false, bool trailingComma = true)
        {
            sb.Append('"').Append(key).Append("\":");
            if (quoted)
                sb.Append('"').Append(Escape(value?.ToString() ?? "")).Append('"');
            else
                sb.Append(Convert.ToString(value, CultureInfo.InvariantCulture));
            if (trailingComma) sb.Append(',');
        }

        private static string Escape(string s) =>
            s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n");

        private static string PhaseToSchema(BattlePhase p) => p switch
        {
            BattlePhase.Warning => "WARNING",
            BattlePhase.Move => "MOVE",
            BattlePhase.Action => "ACTION",
            BattlePhase.Weave => "WEAVE",
            BattlePhase.Resolve => "RESOLVE",
            BattlePhase.Victory => "VICTORY",
            BattlePhase.Defeat => "DEFEAT",
            _ => "MOVE"
        };

        private static BattlePhase PhaseFromSchema(string s) => s?.ToUpperInvariant() switch
        {
            "WARNING" => BattlePhase.Warning,
            "MOVE" => BattlePhase.Move,
            "ACTION" => BattlePhase.Action,
            "WEAVE" => BattlePhase.Weave,
            "RESOLVE" => BattlePhase.Resolve,
            "VICTORY" => BattlePhase.Victory,
            "DEFEAT" => BattlePhase.Defeat,
            _ => BattlePhase.Move
        };

        private static string TelegraphToSchema(TelegraphKind t) => t switch
        {
            TelegraphKind.Slam => "SLAM",
            TelegraphKind.Earthquake => "EARTHQUAKE",
            TelegraphKind.Shrink => "SHRINK",
            TelegraphKind.EarthenFury => "EARTHEN_FURY",
            TelegraphKind.Gale => "GALE",
            TelegraphKind.Spread => "SPREAD",
            TelegraphKind.Stack => "STACK",
            TelegraphKind.Cyclone => "CYCLONE",
            TelegraphKind.IceLance => "ICE_LANCE",
            TelegraphKind.FrozenGround => "FROZEN_GROUND",
            TelegraphKind.IceRing => "ICE_RING",
            TelegraphKind.Blizzard => "BLIZZARD",
            _ => "NONE"
        };

        private static TelegraphKind TelegraphFromSchema(string s) => s?.ToUpperInvariant() switch
        {
            "SLAM" => TelegraphKind.Slam,
            "EARTHQUAKE" => TelegraphKind.Earthquake,
            "SHRINK" => TelegraphKind.Shrink,
            "EARTHEN_FURY" => TelegraphKind.EarthenFury,
            "GALE" => TelegraphKind.Gale,
            "SPREAD" => TelegraphKind.Spread,
            "STACK" => TelegraphKind.Stack,
            "CYCLONE" => TelegraphKind.Cyclone,
            "ICE_LANCE" => TelegraphKind.IceLance,
            "FROZEN_GROUND" => TelegraphKind.FrozenGround,
            "ICE_RING" => TelegraphKind.IceRing,
            "BLIZZARD" => TelegraphKind.Blizzard,
            _ => TelegraphKind.None
        };

        private static string JobToSchema(JobType j) => j switch
        {
            JobType.Knight => "knight",
            JobType.WhiteMage => "white_mage",
            JobType.BlackMage => "black_mage",
            JobType.Bard => "bard",
            _ => "knight"
        };

        private static JobType JobFromSchema(string s) => s switch
        {
            "white_mage" => JobType.WhiteMage,
            "black_mage" => JobType.BlackMage,
            "bard" => JobType.Bard,
            _ => JobType.Knight
        };

        private static string CellToSchema(CellKind c) => c switch
        {
            CellKind.Hazard => "HAZARD",
            CellKind.Safe => "SAFE",
            _ => "NORMAL"
        };

        private static CellKind CellFromSchema(string s) => s?.ToUpperInvariant() switch
        {
            "HAZARD" => CellKind.Hazard,
            "SAFE" => CellKind.Safe,
            _ => CellKind.Normal
        };
    }

    internal static class JsonObjectExtensions
    {
        public static string GetString(this Dictionary<string, object> obj, string key) =>
            obj.TryGetValue(key, out var v) && v is string s ? s : null;

        public static int GetInt(this Dictionary<string, object> obj, string key, int fallback = 0) =>
            obj.TryGetValue(key, out var v) && v is double d ? (int)d : fallback;

        public static bool GetBool(this Dictionary<string, object> obj, string key, bool fallback = false) =>
            obj.TryGetValue(key, out var v) && v is bool b ? b : fallback;

        public static Dictionary<string, object> GetObject(this Dictionary<string, object> obj, string key) =>
            obj.TryGetValue(key, out var v) ? v as Dictionary<string, object> : null;

        public static List<object> GetArray(this Dictionary<string, object> obj, string key) =>
            obj.TryGetValue(key, out var v) ? v as List<object> : null;
    }

    internal static class SimpleJson
    {
        public static Dictionary<string, object> ParseObject(string json)
        {
            var reader = new Reader(json);
            return reader.ReadObject();
        }

        private sealed class Reader
        {
            private readonly string _text;
            private int _pos;

            public Reader(string text) => _text = text ?? "";

            public Dictionary<string, object> ReadObject()
            {
                Expect('{');
                var obj = new Dictionary<string, object>();
                SkipWs();
                if (Peek() == '}') { _pos++; return obj; }
                while (_pos < _text.Length)
                {
                    var key = ReadString();
                    SkipWs();
                    Expect(':');
                    obj[key] = ReadValue();
                    SkipWs();
                    if (Peek() == ',') { _pos++; SkipWs(); continue; }
                    if (Peek() == '}') { _pos++; break; }
                }
                return obj;
            }

            private List<object> ReadArray()
            {
                Expect('[');
                var list = new List<object>();
                SkipWs();
                if (Peek() == ']') { _pos++; return list; }
                while (_pos < _text.Length)
                {
                    list.Add(ReadValue());
                    SkipWs();
                    if (Peek() == ',') { _pos++; SkipWs(); continue; }
                    if (Peek() == ']') { _pos++; break; }
                }
                return list;
            }

            private object ReadValue()
            {
                SkipWs();
                var c = Peek();
                if (c == '{') return ReadObject();
                if (c == '[') return ReadArray();
                if (c == '"') return ReadString();
                if (c == 't' || c == 'f') return ReadBool();
                return ReadNumber();
            }

            private string ReadString()
            {
                Expect('"');
                var sb = new StringBuilder();
                while (_pos < _text.Length)
                {
                    var c = _text[_pos++];
                    if (c == '"') break;
                    if (c == '\\' && _pos < _text.Length)
                    {
                        var esc = _text[_pos++];
                        sb.Append(esc switch
                        {
                            '"' => '"',
                            '\\' => '\\',
                            'n' => '\n',
                            _ => esc
                        });
                    }
                    else sb.Append(c);
                }
                return sb.ToString();
            }

            private double ReadNumber()
            {
                var start = _pos;
                while (_pos < _text.Length && "0123456789.-".IndexOf(_text[_pos]) >= 0) _pos++;
                return double.Parse(_text.Substring(start, _pos - start), CultureInfo.InvariantCulture);
            }

            private bool ReadBool()
            {
                if (Match("true")) return true;
                if (Match("false")) return false;
                throw new FormatException("Invalid boolean at " + _pos);
            }

            private void SkipWs()
            {
                while (_pos < _text.Length && char.IsWhiteSpace(_text[_pos])) _pos++;
            }

            private char Peek() => _pos < _text.Length ? _text[_pos] : '\0';

            private void Expect(char c)
            {
                SkipWs();
                if (_pos >= _text.Length || _text[_pos] != c)
                    throw new FormatException($"Expected '{c}' at {_pos}");
                _pos++;
            }

            private bool Match(string literal)
            {
                if (_text.Substring(_pos, Math.Min(literal.Length, _text.Length - _pos)) == literal)
                {
                    _pos += literal.Length;
                    return true;
                }
                return false;
            }
        }
    }
}
