using System.Collections.Generic;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Mech
{
    public struct MechModelDef
    {
        public MechModelId Id;
        public string Code;
        public string DisplayName;
        public string DisplayNameZh;
        public MechArchetype Archetype;
        public TeamId[] AllowedTeams;
        public float MaxSpeed;
        public float BoostFuel;
        public float MaxHealth;
        public float MaxShield;
        public float PrimaryDps;
        public float SecondaryDamage;
        public float LockRange;
        public float LockCone;
        public Color AccentColor;
        public Vector3 BodyScale;
        public string AbilityId;
        public string Description;
    }

    /// <summary>
    /// Target roster: MS-L1 / MS-H1 / NF-S1 / NF-A1 / NF-C1.
    /// </summary>
    public static class MechModelCatalog
    {
        private static readonly MechModelDef[] All =
        {
            new MechModelDef
            {
                Id = MechModelId.Kestrel,
                Code = "MS-L1",
                DisplayName = "Kestrel",
                DisplayNameZh = "迅影",
                Archetype = MechArchetype.Light,
                AllowedTeams = new[] { TeamId.Terran, TeamId.Orbital, TeamId.Neutral },
                MaxSpeed = 18f,
                BoostFuel = 100f,
                MaxHealth = 100f,
                MaxShield = 50f,
                PrimaryDps = 30f,
                SecondaryDamage = 25f,
                LockRange = 200f,
                LockCone = 15f,
                AccentColor = new Color(0.35f, 0.75f, 0.95f),
                BodyScale = new Vector3(1.6f, 2.6f, 1.2f),
                AbilityId = "boost_dash",
                Description = "高推进轻型机，适合游击与追击"
            },
            new MechModelDef
            {
                Id = MechModelId.Bastion,
                Code = "MS-H1",
                DisplayName = "Bastion",
                DisplayNameZh = "重盾",
                Archetype = MechArchetype.Heavy,
                AllowedTeams = new[] { TeamId.Terran, TeamId.Orbital },
                MaxSpeed = 12f,
                BoostFuel = 70f,
                MaxHealth = 200f,
                MaxShield = 80f,
                PrimaryDps = 45f,
                SecondaryDamage = 30f,
                LockRange = 180f,
                LockCone = 18f,
                AccentColor = new Color(0.25f, 0.45f, 0.32f),
                BodyScale = new Vector3(2.4f, 3.2f, 1.8f),
                AbilityId = "heavy_cannon",
                Description = "重装甲火力平台，适合阵地压制"
            },
            new MechModelDef
            {
                Id = MechModelId.Warden,
                Code = "NF-S1",
                DisplayName = "Warden",
                DisplayNameZh = "守望",
                Archetype = MechArchetype.Support,
                AllowedTeams = new[] { TeamId.Neutral },
                MaxSpeed = 14f,
                BoostFuel = 90f,
                MaxHealth = 110f,
                MaxShield = 70f,
                PrimaryDps = 18f,
                SecondaryDamage = 15f,
                LockRange = 160f,
                LockCone = 20f,
                AccentColor = new Color(0.55f, 0.85f, 0.95f),
                BodyScale = new Vector3(1.8f, 2.8f, 1.4f),
                AbilityId = "repair_beam",
                Description = "近距修复光束，跟队护航支援"
            },
            new MechModelDef
            {
                Id = MechModelId.Mediator,
                Code = "NF-A1",
                DisplayName = "Mediator",
                DisplayNameZh = "仲裁",
                Archetype = MechArchetype.Balanced,
                AllowedTeams = new[] { TeamId.Neutral },
                MaxSpeed = 15f,
                BoostFuel = 85f,
                MaxHealth = 140f,
                MaxShield = 90f,
                PrimaryDps = 32f,
                SecondaryDamage = 22f,
                LockRange = 190f,
                LockCone = 16f,
                AccentColor = new Color(0.7f, 0.78f, 0.95f),
                BodyScale = new Vector3(2.0f, 2.9f, 1.5f),
                AbilityId = "phase_projector",
                Description = "相位护盾投射，交火克制"
            },
            new MechModelDef
            {
                Id = MechModelId.Beacon,
                Code = "NF-C1",
                DisplayName = "Beacon",
                DisplayNameZh = "航标",
                Archetype = MechArchetype.Scout,
                AllowedTeams = new[] { TeamId.Neutral },
                MaxSpeed = 20f,
                BoostFuel = 110f,
                MaxHealth = 80f,
                MaxShield = 40f,
                PrimaryDps = 22f,
                SecondaryDamage = 18f,
                LockRange = 260f,
                LockCone = 22f,
                AccentColor = new Color(0.9f, 0.92f, 1f),
                BodyScale = new Vector3(1.4f, 2.3f, 1.1f),
                AbilityId = "sensor_ping",
                Description = "高传感器侦察机，航道标示"
            }
        };

        public static IReadOnlyList<MechModelDef> GetAll() => All;

        public static MechModelDef Get(MechModelId id)
        {
            for (var i = 0; i < All.Length; i++)
            {
                if (All[i].Id == id)
                {
                    return All[i];
                }
            }

            return All[0];
        }

        public static MechModelDef FromArchetype(MechArchetype archetype)
        {
            switch (archetype)
            {
                case MechArchetype.Heavy:
                    return Get(MechModelId.Bastion);
                case MechArchetype.Support:
                    return Get(MechModelId.Warden);
                case MechArchetype.Balanced:
                    return Get(MechModelId.Mediator);
                case MechArchetype.Scout:
                    return Get(MechModelId.Beacon);
                default:
                    return Get(MechModelId.Kestrel);
            }
        }

        public static MechModelId DefaultForTeam(TeamId team)
        {
            switch (team)
            {
                case TeamId.Terran:
                    return MechModelId.Bastion;
                case TeamId.Orbital:
                    return MechModelId.Kestrel;
                case TeamId.Neutral:
                    return MechModelId.Mediator;
                default:
                    return MechModelId.Kestrel;
            }
        }

        public static List<MechModelDef> GetForTeam(TeamId team)
        {
            var list = new List<MechModelDef>();
            foreach (var def in All)
            {
                if (def.AllowedTeams == null)
                {
                    continue;
                }

                foreach (var t in def.AllowedTeams)
                {
                    if (t == team)
                    {
                        list.Add(def);
                        break;
                    }
                }
            }

            if (list.Count == 0)
            {
                list.Add(Get(MechModelId.Kestrel));
            }

            return list;
        }

        public static string FormatOption(MechModelDef def)
        {
            return $"{def.Code} {def.DisplayNameZh} {def.DisplayName}";
        }

        public static MechStats ToStats(MechModelDef def)
        {
            return new MechStats
            {
                MaxSpeed = def.MaxSpeed,
                BoostFuel = def.BoostFuel,
                MaxHealth = def.MaxHealth,
                MaxShield = def.MaxShield
            };
        }
    }
}
