using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Persists last selected boss across sessions (Quest / Editor).
    /// </summary>
    public static class BattleBossPrefs
    {
        private const string BossKey = "aetherboard.boss.id";

        public static string LoadBoss(string fallback = "earth")
        {
            if (!PlayerPrefs.HasKey(BossKey)) return Normalize(fallback);
            return Normalize(PlayerPrefs.GetString(BossKey, fallback));
        }

        public static void SaveBoss(string bossId)
        {
            if (string.IsNullOrWhiteSpace(bossId)) return;
            PlayerPrefs.SetString(BossKey, Normalize(bossId));
            PlayerPrefs.Save();
        }

        private static string Normalize(string bossId)
        {
            foreach (var id in BossRegistry.AllBossIds)
            {
                if (id == bossId) return id;
            }
            return "earth";
        }
    }
}
