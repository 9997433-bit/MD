using System;
using System.Collections;
using CosmicFront.UI;
using UnityEngine;

namespace CosmicFront.Steam
{
    /// <summary>
    /// Reads launch arg <c>-cosmicJoin=cosmicfront://join?ip=x&amp;port=7770</c>,
    /// fills the hangar address field, and optionally auto-Joins.
    /// </summary>
    public class SteamInviteBootstrap : MonoBehaviour
    {
        public const string CmdArgPrefix = "-cosmicJoin=";

        [SerializeField] private bool autoJoin = true;
        [SerializeField] private float autoJoinDelaySeconds = 0.35f;

        public string JoinUrl { get; private set; }
        public bool HasPendingInvite { get; private set; }
        public bool DidAutoJoin { get; private set; }

        private void Awake()
        {
            EnsureSteamManager();
            TryConsumeCommandLine();
        }

        private void Start()
        {
            if (!HasPendingInvite)
            {
                return;
            }

            StartCoroutine(ApplyInviteRoutine());
        }

        public static string FindCosmicJoinArg(string[] args)
        {
            if (args == null)
            {
                return null;
            }

            for (var i = 0; i < args.Length; i++)
            {
                var arg = args[i];
                if (string.IsNullOrEmpty(arg))
                {
                    continue;
                }

                if (arg.StartsWith(CmdArgPrefix, StringComparison.OrdinalIgnoreCase))
                {
                    return arg.Substring(CmdArgPrefix.Length).Trim().Trim('"', '\'');
                }

                if (string.Equals(arg, "-cosmicJoin", StringComparison.OrdinalIgnoreCase) &&
                    i + 1 < args.Length)
                {
                    return args[i + 1]?.Trim().Trim('"', '\'');
                }
            }

            return null;
        }

        private void TryConsumeCommandLine()
        {
            var url = FindCosmicJoinArg(Environment.GetCommandLineArgs());
            if (string.IsNullOrWhiteSpace(url))
            {
                return;
            }

            JoinUrl = url;
            if (SteamManager.Instance != null)
            {
                SteamManager.Instance.SetPendingJoinUrl(url);
            }

            if (SteamManager.ParseJoinUrl(url, out _, out _))
            {
                HasPendingInvite = true;
                Debug.Log($"[SteamInviteBootstrap] Pending invite: {url}");
            }
            else
            {
                Debug.LogWarning($"[SteamInviteBootstrap] Invalid -cosmicJoin URL: {url}");
            }
        }

        private IEnumerator ApplyInviteRoutine()
        {
            // Wait one frame so HangarMenu Start() can create defaults.
            yield return null;

            if (SteamManager.Instance == null ||
                !SteamManager.Instance.TryGetJoinEndpoint(out var ip, out var port))
            {
                yield break;
            }

            var menu = FindObjectOfType<HangarMenu>();
            if (menu == null)
            {
                Debug.LogWarning("[SteamInviteBootstrap] HangarMenu not found; invite not applied.");
                yield break;
            }

            menu.ApplyJoinEndpoint(ip, port);
            Debug.Log($"[SteamInviteBootstrap] Filled join endpoint {ip}:{port}");

            if (!autoJoin)
            {
                yield break;
            }

            if (autoJoinDelaySeconds > 0f)
            {
                yield return new WaitForSeconds(autoJoinDelaySeconds);
            }

            menu.TriggerJoin();
            DidAutoJoin = true;
            Debug.Log("[SteamInviteBootstrap] Auto Join triggered.");
        }

        private static void EnsureSteamManager()
        {
            if (SteamManager.Instance != null)
            {
                return;
            }

            var existing = FindObjectOfType<SteamManager>();
            if (existing != null)
            {
                return;
            }

            var go = new GameObject("SteamManager");
            go.AddComponent<SteamManager>();
        }
    }
}
