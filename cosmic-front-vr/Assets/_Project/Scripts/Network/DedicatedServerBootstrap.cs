using System.Linq;
using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Network;

namespace CosmicFront.Network
{
    /// <summary>
    /// Auto-starts Fish-Net dedicated server when launched with -cosmicServer.
    /// Place on the same GameObject as NetworkManager (created by Setup All Scenes).
    /// </summary>
    public class DedicatedServerBootstrap : MonoBehaviour
    {
        [SerializeField] private string battleScene = "Map_ColonyRim";
        [SerializeField] private bool autoStartInBatchMode = true;

        private void Start()
        {
            if (!ShouldRunDedicatedServer())
            {
                return;
            }

            Debug.Log("[DedicatedServer] Starting headless server...");
            NetworkBootstrap.StartDedicatedServer(battleScene, OnServerReady);
        }

        private bool ShouldRunDedicatedServer()
        {
            var args = System.Environment.GetCommandLineArgs();
            if (args.Contains("-cosmicServer"))
            {
                return true;
            }

#if UNITY_SERVER
            return autoStartInBatchMode && Application.isBatchMode;
#else
            return false;
#endif
        }

        private void OnServerReady()
        {
            Debug.Log($"[DedicatedServer] Loading {battleScene}");
            NetworkBootstrap.LoadBattleScene(battleScene);
        }
    }
}
