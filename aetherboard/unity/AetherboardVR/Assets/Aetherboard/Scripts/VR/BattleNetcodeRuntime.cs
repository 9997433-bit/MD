using System;
using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Detects Unity Netcode for GameObjects at runtime (optional package).
    /// </summary>
    public static class BattleNetcodeRuntime
    {
        private static bool _probed;
        private static bool _available;

        public static bool IsAvailable
        {
            get
            {
                if (!_probed) Probe();
                return _available;
            }
        }

        public static string StatusMessage { get; private set; } = "Not probed";

        private static void Probe()
        {
            _probed = true;
            var netcodeType = Type.GetType("Unity.Netcode.NetworkManager, Unity.Netcode.Runtime");
            if (netcodeType != null)
            {
                _available = true;
                StatusMessage = "Unity Netcode package detected";
                return;
            }

            _available = false;
            StatusMessage = "Unity Netcode not installed — using WebSocket relay";
        }

        public static void LogStatus()
        {
            Probe();
            Debug.Log($"[Aetherboard] Netcode: {StatusMessage}");
        }
    }
}
