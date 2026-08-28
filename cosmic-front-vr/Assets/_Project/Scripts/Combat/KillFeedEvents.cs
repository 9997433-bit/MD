using System;
using UnityEngine;

namespace CosmicFront.Combat
{
    /// <summary>
    /// Decoupled kill-feed bus. UI and streak systems subscribe; combat/network raise.
    /// </summary>
    public static class KillFeedEvents
    {
        public static event Action<string, string, string> OnKill;

        public static void Raise(string killerName, string victimName, string weapon)
        {
            OnKill?.Invoke(
                string.IsNullOrWhiteSpace(killerName) ? "?" : killerName,
                string.IsNullOrWhiteSpace(victimName) ? "?" : victimName,
                string.IsNullOrWhiteSpace(weapon) ? "武器" : weapon);
        }

        public static string ResolveDisplayName(GameObject go)
        {
            if (go == null)
            {
                return "?";
            }

            var root = go.transform.root != null ? go.transform.root.gameObject : go;
            return root.name.Replace("(Clone)", string.Empty).Trim();
        }
    }
}
