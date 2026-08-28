using System;
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

        [SerializeField] private bool initializeOnAwake = true;
        [SerializeField] private uint appId = 480; // Spacewar placeholder for testing

        public bool IsInitialized { get; private set; }
        public bool IsOfflineFallback { get; private set; }
        public string PersonaName { get; private set; } = "Pilot";
        public ulong SteamId { get; private set; }

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
            return $"cosmicfront://join?ip={hostAddress}&port={port}";
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
