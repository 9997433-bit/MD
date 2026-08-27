#if AETHERBOARD_NGO_INSTALLED
using System;
using Unity.Netcode;
using UnityEngine;

namespace Aetherboard.NetcodeIntegration
{
    /// <summary>
    /// Attach alongside NetworkManager — forwards NGO messages to BattleNetcodeService in VR layer.
    /// </summary>
    public class BattleNetcodeHostCoordinator : NetworkBehaviour
    {
        public static event Action<string> OnRemoteBattleMessage;

        public override void OnNetworkSpawn()
        {
            BattleNetcodeFacade.Register(json => OnRemoteBattleMessage?.Invoke(json));
            Debug.Log($"[Aetherboard] NGO coordinator active ({(IsServer ? "host" : "client")})");
        }

        public override void OnNetworkDespawn()
        {
            BattleNetcodeFacade.Unregister();
        }

        public static void BroadcastState(string json) => BattleNetcodeFacade.SendToAll(json);
    }
}
#else
namespace Aetherboard.NetcodeIntegration
{
    /// <summary>Stub NetworkBehaviour placeholder when NGO is not installed.</summary>
    public class BattleNetcodeHostCoordinator : UnityEngine.MonoBehaviour
    {
        public static event System.Action<string> OnRemoteBattleMessage;
        public static void BroadcastState(string json) { }
    }
}
#endif
