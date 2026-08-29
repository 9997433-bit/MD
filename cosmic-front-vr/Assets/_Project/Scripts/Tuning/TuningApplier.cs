using UnityEngine;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.Tuning
{
    /// <summary>
    /// Aggregates equipped passive mods and applies them to mech systems.
    /// Call after archetype Configure so multipliers stack on base stats.
    /// </summary>
    public static class TuningApplier
    {
        public struct AggregatedTuning
        {
            public float MoveSpeedMultiplier;
            public float ShieldMultiplier;
            public float HealthMultiplier;
            public float BoostFuelMultiplier;
            /// <summary>Multiplier applied to weapon cooldown duration (e.g. 0.95 = -5%).</summary>
            public float CooldownMultiplier;

            public static AggregatedTuning Identity => new AggregatedTuning
            {
                MoveSpeedMultiplier = 1f,
                ShieldMultiplier = 1f,
                HealthMultiplier = 1f,
                BoostFuelMultiplier = 1f,
                CooldownMultiplier = 1f
            };
        }

        public static AggregatedTuning Aggregate(PilotLoadout loadout)
        {
            var result = AggregatedTuning.Identity;
            if (loadout == null)
            {
                return result;
            }

            var slots = loadout.GetEquippedSnapshot();
            for (var i = 0; i < slots.Length; i++)
            {
                var mod = slots[i];
                if (mod == null)
                {
                    continue;
                }

                switch (mod.Stat)
                {
                    case PassiveModStat.MoveSpeedPercent:
                        result.MoveSpeedMultiplier += mod.Value;
                        break;
                    case PassiveModStat.ShieldPercent:
                        result.ShieldMultiplier += mod.Value;
                        break;
                    case PassiveModStat.HealthPercent:
                        result.HealthMultiplier += mod.Value;
                        break;
                    case PassiveModStat.BoostFuelPercent:
                        result.BoostFuelMultiplier += mod.Value;
                        break;
                    case PassiveModStat.CooldownPercent:
                        result.CooldownMultiplier += mod.Value;
                        break;
                }
            }

            result.MoveSpeedMultiplier = Mathf.Max(0.01f, result.MoveSpeedMultiplier);
            result.ShieldMultiplier = Mathf.Max(0.01f, result.ShieldMultiplier);
            result.HealthMultiplier = Mathf.Max(0.01f, result.HealthMultiplier);
            result.BoostFuelMultiplier = Mathf.Max(0.01f, result.BoostFuelMultiplier);
            result.CooldownMultiplier = Mathf.Max(0.01f, result.CooldownMultiplier);
            return result;
        }

        public static void Apply(MechController mech, PilotLoadout loadout)
        {
            if (mech == null || loadout == null || !loadout.HasAnyMod())
            {
                return;
            }

            Apply(mech, Aggregate(loadout));
        }

        public static void Apply(MechController mech, AggregatedTuning tuning)
        {
            if (mech == null)
            {
                return;
            }

            var movement = mech.GetComponent<MechMovement>();
            var health = mech.GetComponent<HealthSystem>();
            var primary = mech.GetComponent<WeaponPrimary>();
            var secondary = mech.GetComponent<WeaponSecondary>();

            movement?.ApplyTuning(tuning.MoveSpeedMultiplier, tuning.BoostFuelMultiplier);

            if (health != null)
            {
                var hp = health.MaxHealth * tuning.HealthMultiplier;
                var shield = health.MaxShield * tuning.ShieldMultiplier;
                health.Configure(health.Team, hp, shield);
            }

            primary?.ApplyCooldownMultiplier(tuning.CooldownMultiplier);
            secondary?.ApplyCooldownMultiplier(tuning.CooldownMultiplier);
        }
    }
}
