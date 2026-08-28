using System;
using UnityEngine;

namespace CosmicFront.Tuning
{
    public enum PassiveModStat
    {
        MoveSpeedPercent,
        ShieldPercent,
        CooldownPercent,
        HealthPercent,
        BoostFuelPercent
    }

    /// <summary>
    /// Serializable passive mod definition (Scriptable-like data, no asset required).
    /// Percent values use fractions: +5% = 0.05, cooldown -5% = -0.05.
    /// </summary>
    [Serializable]
    public class PassiveMod
    {
        [SerializeField] private string id;
        [SerializeField] private string displayName;
        [SerializeField] private string description;
        [SerializeField] private int cost = 1;
        [SerializeField] private PassiveModStat stat;
        [SerializeField] private float value;

        public string Id => id;
        public string DisplayName => displayName;
        public string Description => description;
        public int Cost => cost;
        public PassiveModStat Stat => stat;
        public float Value => value;

        public PassiveMod()
        {
        }

        public PassiveMod(string id, string displayName, string description, int cost, PassiveModStat stat, float value)
        {
            this.id = id;
            this.displayName = displayName;
            this.description = description;
            this.cost = Mathf.Max(0, cost);
            this.stat = stat;
            this.value = value;
        }

        public static readonly PassiveMod MoveSpeedPlus5 = new PassiveMod(
            "move_speed_5",
            "推进强化",
            "移速 +5%",
            1,
            PassiveModStat.MoveSpeedPercent,
            0.05f);

        public static readonly PassiveMod ShieldPlus10 = new PassiveMod(
            "shield_10",
            "护盾增幅",
            "护盾 +10%",
            1,
            PassiveModStat.ShieldPercent,
            0.10f);

        public static readonly PassiveMod CooldownMinus5 = new PassiveMod(
            "cooldown_5",
            "散热优化",
            "武器冷却 -5%",
            1,
            PassiveModStat.CooldownPercent,
            -0.05f);

        public static readonly PassiveMod HealthPlus10 = new PassiveMod(
            "health_10",
            "装甲强化",
            "生命 +10%",
            2,
            PassiveModStat.HealthPercent,
            0.10f);

        public static readonly PassiveMod BoostPlus15 = new PassiveMod(
            "boost_15",
            "推进剂扩容",
            "推进燃料 +15%",
            1,
            PassiveModStat.BoostFuelPercent,
            0.15f);

        public static PassiveMod[] Catalog => new[]
        {
            MoveSpeedPlus5,
            ShieldPlus10,
            CooldownMinus5,
            HealthPlus10,
            BoostPlus15
        };

        public static PassiveMod FindById(string modId)
        {
            if (string.IsNullOrEmpty(modId))
            {
                return null;
            }

            foreach (var mod in Catalog)
            {
                if (mod != null && mod.id == modId)
                {
                    return mod;
                }
            }

            return null;
        }
    }
}
