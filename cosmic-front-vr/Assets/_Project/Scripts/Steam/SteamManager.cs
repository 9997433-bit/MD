using System;
using CosmicFront.Network;
using UnityEngine;

namespace CosmicFront.Steam
{
    /// <summary>
    /// Steamworks integration scaffold. Works offline without Steamworks.NET.
    /// When Steamworks.NET is imported, define COSMIC_STEAMWORKS and wire real API calls.
    /// </summary>
    public class SteamManager : MonoBehaviour
    {
        public static SteamManager Instance { get; private set; }

        public const string JoinScheme = "cosmicfront";
        public const string JoinHost = "join";

        [SerializeField] private bool initializeOnAwake = true;
        [SerializeField] private uint appId = 480; // Spacewar placeholder for testing

        public bool IsInitialized { get; private set; }
        public bool IsOfflineFallback { get; private set; }
        public string PersonaName { get; private set; } = "Pilot";
        public ulong SteamId { get; private set; }

        /// <summary>Pending invite deep-link URL (e.g. from -cosmicJoin=).</summary>
        public string PendingJoinUrl { get; private set; }

        public event Action Initialized;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);

            if (initializeOnAwake)
            {
                Initialize();
            }
        }

        public void Initialize()
        {
            if (IsInitialized)
            {
                return;
            }

#if COSMIC_STEAMWORKS
            try
            {
                // Placeholder for SteamAPI.Init() when Steamworks.NET is present.
                // SteamAPI.Init();
                // PersonaName = SteamFriends.GetPersonaName();
                // SteamId = SteamUser.GetSteamID().m_SteamID;
                IsInitialized = true;
                IsOfflineFallback = false;
                Debug.Log("[SteamManager] COSMIC_STEAMWORKS build — wire Steamworks.NET here.");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[SteamManager] Steam init failed, offline fallback. {e.Message}");
                UseOfflineFallback();
            }
#else
            UseOfflineFallback();
#endif
            Initialized?.Invoke();
        }

        private void UseOfflineFallback()
        {
            IsInitialized = true;
            IsOfflineFallback = true;
            PersonaName = Environment.UserName;
            SteamId = 0;
            Debug.Log($"[SteamManager] Offline mode as '{PersonaName}'. Import Steamworks.NET + define COSMIC_STEAMWORKS for Steam.");
        }

        public string GetInviteConnectString(string hostAddress, ushort port)
        {
            return $"{JoinScheme}://{JoinHost}?ip={hostAddress}&port={port}";
        }

        public void SetPendingJoinUrl(string url)
        {
            PendingJoinUrl = string.IsNullOrWhiteSpace(url) ? null : url.Trim();
        }

        /// <summary>
        /// Parses <c>cosmicfront://join?ip=x&amp;port=7770</c> (also accepts bare query or ip:port).
        /// </summary>
        public static bool ParseJoinUrl(string url, out string ip, out ushort port)
        {
            ip = null;
            port = NetworkSessionConfig.Port;

            if (string.IsNullOrWhiteSpace(url))
            {
                return false;
            }

            var raw = url.Trim().Trim('"', '\'');

            // Bare "ip:port"
            if (raw.IndexOf("://", StringComparison.Ordinal) < 0 && raw.IndexOf('?') < 0)
            {
                return TryParseHostPort(raw, out ip, out port);
            }

            string query = null;
            try
            {
                var uri = new Uri(raw);
                if (!string.Equals(uri.Scheme, JoinScheme, StringComparison.OrdinalIgnoreCase))
                {
                    return false;
                }

                query = uri.Query;
            }
            catch (UriFormatException)
            {
                var qIndex = raw.IndexOf('?');
                if (qIndex < 0)
                {
                    return false;
                }

                query = raw.Substring(qIndex);
            }

            if (string.IsNullOrEmpty(query))
            {
                return false;
            }

            if (query[0] == '?')
            {
                query = query.Substring(1);
            }

            string parsedIp = null;
            ushort parsedPort = NetworkSessionConfig.Port;
            var hasIp = false;

            foreach (var part in query.Split('&'))
            {
                if (string.IsNullOrEmpty(part))
                {
                    continue;
                }

                var eq = part.IndexOf('=');
                var key = eq >= 0 ? part.Substring(0, eq) : part;
                var value = eq >= 0 ? Uri.UnescapeDataString(part.Substring(eq + 1)) : string.Empty;

                if (string.Equals(key, "ip", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(key, "address", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(key, "host", StringComparison.OrdinalIgnoreCase))
                {
                    if (!string.IsNullOrWhiteSpace(value))
                    {
                        parsedIp = value.Trim();
                        hasIp = true;
                    }
                }
                else if (string.Equals(key, "port", StringComparison.OrdinalIgnoreCase))
                {
                    if (ushort.TryParse(value, out var p) && p > 0)
                    {
                        parsedPort = p;
                    }
                }
            }

            if (!hasIp)
            {
                return false;
            }

            ip = parsedIp;
            port = parsedPort;
            return true;
        }

        /// <summary>Returns the pending join endpoint if <see cref="PendingJoinUrl"/> was set and valid.</summary>
        public bool TryGetJoinEndpoint(out string ip, out ushort port)
        {
            return ParseJoinUrl(PendingJoinUrl, out ip, out port);
        }

        private static bool TryParseHostPort(string raw, out string ip, out ushort port)
        {
            ip = null;
            port = NetworkSessionConfig.Port;

            var colon = raw.LastIndexOf(':');
            if (colon > 0 && colon < raw.Length - 1 &&
                ushort.TryParse(raw.Substring(colon + 1), out var p) && p > 0)
            {
                ip = raw.Substring(0, colon).Trim();
                port = p;
                return !string.IsNullOrWhiteSpace(ip);
            }

            if (string.IsNullOrWhiteSpace(raw))
            {
                return false;
            }

            ip = raw.Trim();
            return true;
        }

        public void OpenInviteOverlayPlaceholder()
        {
            if (IsOfflineFallback)
            {
                Debug.Log("[SteamManager] Invite overlay unavailable offline. Share LAN IP instead.");
                return;
            }

            Debug.Log("[SteamManager] TODO: SteamFriends.ActivateGameOverlayInviteDialog");
        }

#if COSMIC_STEAMWORKS
        private void Update()
        {
            // SteamAPI.RunCallbacks();
        }

        private void OnDestroy()
        {
            // SteamAPI.Shutdown();
        }
#endif
    }
}
