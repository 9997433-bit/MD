#if AETHERBOARD_NGO_INSTALLED
using Unity.Netcode;
using UnityEngine;

namespace Aetherboard.NetcodeIntegration
{
    /// <summary>
    /// Ensures BattleNetcodeHostCoordinator is present when NGO starts.
    /// </summary>
    internal static class BattleNetcodeNGOSetup
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void HookNetworkManager()
        {
            NetworkManager.OnInstantiated += OnNetworkManagerInstantiated;
        }

        private static void OnNetworkManagerInstantiated(NetworkManager nm)
        {
            if (nm == null) return;
            EnsureCoordinator(nm);
            nm.OnServerStarted += () => EnsureCoordinator(nm);
            nm.OnClientStarted += () => EnsureCoordinator(nm);
        }

        private static void EnsureCoordinator(NetworkManager nm)
        {
            if (nm.GetComponent<BattleNetcodeHostCoordinator>() != null) return;
            nm.gameObject.AddComponent<BattleNetcodeHostCoordinator>();
        }
    }
}
#endif
