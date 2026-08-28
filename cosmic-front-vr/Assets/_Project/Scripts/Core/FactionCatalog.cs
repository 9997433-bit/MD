using UnityEngine;

namespace CosmicFront.Core
{
    /// <summary>
    /// Display names, primary colors, and default mech bias for each TeamId.
    /// </summary>
    public static class FactionCatalog
    {
        public readonly struct FactionInfo
        {
            public readonly TeamId Id;
            public readonly string DisplayName;
            public readonly string Code;
            public readonly Color PrimaryColor;
            public readonly MechArchetype DefaultArchetype;

            public FactionInfo(
                TeamId id,
                string displayName,
                string code,
                Color primaryColor,
                MechArchetype defaultArchetype)
            {
                Id = id;
                DisplayName = displayName;
                Code = code;
                PrimaryColor = primaryColor;
                DefaultArchetype = defaultArchetype;
            }
        }

        private static readonly FactionInfo TerranInfo = new(
            TeamId.Terran,
            "地球联合军",
            "TU",
            new Color(0.18f, 0.42f, 0.28f),
            MechArchetype.Heavy);

        private static readonly FactionInfo OrbitalInfo = new(
            TeamId.Orbital,
            "轨道联盟",
            "OL",
            new Color(0.55f, 0.35f, 0.72f),
            MechArchetype.Light);

        private static readonly FactionInfo NeutralInfo = new(
            TeamId.Neutral,
            "维和舰队",
            "NF",
            new Color(0.72f, 0.82f, 0.95f),
            MechArchetype.Light);

        private static readonly FactionInfo NoneInfo = new(
            TeamId.None,
            "无阵营",
            "—",
            Color.gray,
            MechArchetype.Light);

        public static FactionInfo Get(TeamId team)
        {
            switch (team)
            {
                case TeamId.Terran:
                    return TerranInfo;
                case TeamId.Orbital:
                    return OrbitalInfo;
                case TeamId.Neutral:
                    return NeutralInfo;
                default:
                    return NoneInfo;
            }
        }

        public static string GetDisplayName(TeamId team) => Get(team).DisplayName;

        public static Color GetPrimaryColor(TeamId team) => Get(team).PrimaryColor;

        public static MechArchetype GetDefaultArchetype(TeamId team) => Get(team).DefaultArchetype;
    }
}
