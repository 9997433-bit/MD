using System.Collections.Generic;

namespace Aetherboard.Core
{
    public static class SkillCatalog
    {
        public static readonly Dictionary<string, SkillDef> Skills = new()
        {
            ["shield_bash"] = new SkillDef { Id = "shield_bash", Name = "盾击", Kind = "gcd", Range = 1, Power = 80 },
            ["rampart"] = new SkillDef { Id = "rampart", Name = "铁壁", Kind = "ogcd", Range = 0, MitDuration = 2 },
            ["provoke"] = new SkillDef { Id = "provoke", Name = "挑衅", Kind = "ogcd", Range = 7 },
            ["cure"] = new SkillDef { Id = "cure", Name = "治疗", Kind = "gcd", Range = 7, Heal = 180 },
            ["medica"] = new SkillDef { Id = "medica", Name = "医技", Kind = "gcd", Range = 7, Heal = 90, AoeRadius = 2 },
            ["benediction"] = new SkillDef { Id = "benediction", Name = "天赐", Kind = "ogcd", Range = 7, Heal = 9999 },
            ["fire"] = new SkillDef { Id = "fire", Name = "火炎", Kind = "gcd", Range = 7, Power = 140 },
            ["blizzard"] = new SkillDef { Id = "blizzard", Name = "冰结", Kind = "gcd", Range = 7, Power = 70 },
            ["manaward"] = new SkillDef { Id = "manaward", Name = "魔罩", Kind = "ogcd", Range = 0, MitDuration = 2 },
            ["straight_shot"] = new SkillDef { Id = "straight_shot", Name = "强力射击", Kind = "gcd", Range = 7, Power = 95 },
            ["mages_ballad"] = new SkillDef { Id = "mages_ballad", Name = "魔人歌", Kind = "ogcd", Range = 0 },
            ["repelling_shot"] = new SkillDef { Id = "repelling_shot", Name = "后跃射", Kind = "ogcd", Range = 7, Power = 40 },
            ["interrupt"] = new SkillDef { Id = "interrupt", Name = "打断", Kind = "ogcd", Range = 7 },
        };

        public static SkillDef Get(string id) => Skills[id];
    }

    public static class JobCatalog
    {
        public static readonly Dictionary<JobType, int> MoveRange = new()
        {
            [JobType.Knight] = 1,
            [JobType.WhiteMage] = 1,
            [JobType.BlackMage] = 1,
            [JobType.Bard] = 2,
        };

        public static readonly Dictionary<JobType, string[]> JobSkills = new()
        {
            [JobType.Knight] = new[] { "shield_bash", "rampart", "provoke" },
            [JobType.WhiteMage] = new[] { "cure", "medica", "benediction" },
            [JobType.BlackMage] = new[] { "fire", "blizzard", "manaward" },
            [JobType.Bard] = new[] { "straight_shot", "mages_ballad", "repelling_shot" },
        };

        public static List<UnitState> CreateParty()
        {
            return new List<UnitState>
            {
                new() { Id = "knight", DisplayName = "铁卫", Job = JobType.Knight, Pos = new GridPos(3, 5), Hp = 1200, MaxHp = 1200 },
                new() { Id = "white_mage", DisplayName = "白愈", Job = JobType.WhiteMage, Pos = new GridPos(2, 5), Hp = 900, MaxHp = 900 },
                new() { Id = "black_mage", DisplayName = "黑炎", Job = JobType.BlackMage, Pos = new GridPos(4, 5), Hp = 800, MaxHp = 800 },
                new() { Id = "bard", DisplayName = "游弦", Job = JobType.Bard, Pos = new GridPos(3, 4), Hp = 850, MaxHp = 850 },
            };
        }
    }
}
