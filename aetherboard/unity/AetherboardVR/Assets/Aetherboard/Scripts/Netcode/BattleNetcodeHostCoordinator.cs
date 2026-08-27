#if AETHERBOARD_NGO_INSTALLED
using System;
using Unity.Netcode;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.NetcodeIntegration
{
    /// <summary>
    /// Attach alongside NetworkManager — forwards NGO messages to VR battle session.
    /// </summary>
    public class BattleNetcodeHostCoordinator : NetworkBehaviour
    {
        public static event Action<string> OnRemoteBattleMessage;

        /// <summary>Host command ingress — return error message or null on success.</summary>
        public static Func<string, ulong, string> OnCommandReceived;

        /// <summary>Lines to send to a newly connected NGO client (welcome, initial state).</summary>
        public static Func<string[]> GetInitialHandshake;

        private static bool _clientHooked;

        public override void OnNetworkSpawn()
        {
            BattleNetcodeFacade.RegisterSync(json => OnRemoteBattleMessage?.Invoke(json));
            if (IsServer)
            {
                BattleNetcodeFacade.RegisterCommandHandler(HandleCommand);
                HookClientConnect();
            }

            Debug.Log($"[Aetherboard] NGO coordinator active ({(IsServer ? "host" : "client")})");
        }

        public override void OnNetworkDespawn()
        {
            BattleNetcodeFacade.Unregister();
            if (IsServer && NetworkManager.Singleton != null)
                NetworkManager.Singleton.OnClientConnectedCallback -= OnClientConnected;
            _clientHooked = false;
        }

        public static void BroadcastState(string json) => BattleNetcodeFacade.SendToAll(json);

        private static void HookClientConnect()
        {
            if (_clientHooked || NetworkManager.Singleton == null) return;
            NetworkManager.Singleton.OnClientConnectedCallback += OnClientConnected;
            _clientHooked = true;
        }

        private static void OnClientConnected(ulong clientId)
        {
            if (NetworkManager.Singleton == null || !NetworkManager.Singleton.IsServer) return;
            var lines = GetInitialHandshake?.Invoke();
            if (lines == null) return;

            foreach (var line in lines)
            {
                if (!string.IsNullOrEmpty(line))
                    BattleNetcodeFacade.SendToClient(clientId, line);
            }
        }

        private static void HandleCommand(string json, ulong clientId)
        {
            var error = OnCommandReceived?.Invoke(json, clientId);
            if (!string.IsNullOrEmpty(error))
                BattleNetcodeFacade.SendToClient(clientId, BattleSyncProtocol.EncodeError(error));
        }
    }
}
#else
namespace Aetherboard.NetcodeIntegration
{
    /// <summary>Stub NetworkBehaviour placeholder when NGO is not installed.</summary>
    public class BattleNetcodeHostCoordinator : UnityEngine.MonoBehaviour
    {
        public static event System.Action<string> OnRemoteBattleMessage;
        public static System.Func<string, ulong, string> OnCommandReceived;
        public static System.Func<string[]> GetInitialHandshake;
        public static void BroadcastState(string json) { }
    }
}
#endif
