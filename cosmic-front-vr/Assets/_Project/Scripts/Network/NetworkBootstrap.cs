using System;
using FishNet;
using FishNet.Managing;
using FishNet.Managing.Scened;
using FishNet.Transporting;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace CosmicFront.Network
{
    /// <summary>
    /// Fish-Net LAN Host / Client bootstrap. Requires a NetworkManager in the scene (see Setup All Scenes).
    /// </summary>
    public static class NetworkBootstrap
    {
        public static bool IsOnlineReady => InstanceFinder.NetworkManager != null;

        public static bool IsServer => InstanceFinder.NetworkManager != null &&
                                       InstanceFinder.NetworkManager.IsServerStarted;

        public static bool IsClient => InstanceFinder.NetworkManager != null &&
                                       InstanceFinder.NetworkManager.IsClientStarted;

        public static event Action<string> StatusChanged;

        public static void StartHost(Action onConnected)
        {
            var nm = RequireNetworkManager();
            if (nm == null)
            {
                return;
            }

            SubscribeOnce(nm, onConnected);
            RaiseStatus("正在启动 Host...");

            if (!nm.ServerManager.StartConnection())
            {
                RaiseStatus("Host 启动失败：Server");
                return;
            }

            if (!nm.ClientManager.StartConnection())
            {
                RaiseStatus("Host 启动失败：Client");
            }
        }

        public static void StartClient(string address, Action onConnected)
        {
            var nm = RequireNetworkManager();
            if (nm == null)
            {
                return;
            }

            SubscribeOnce(nm, onConnected);
            RaiseStatus($"正在连接 {address}...");

            if (!nm.ClientManager.StartConnection(address, NetworkSessionConfig.Port))
            {
                RaiseStatus("Client 连接失败");
            }
        }

        public static void LoadBattleScene(string sceneName)
        {
            var nm = InstanceFinder.NetworkManager;
            if (nm == null || !nm.IsServerStarted)
            {
                return;
            }

            RaiseStatus($"服务器载入 {sceneName}...");
            var loadData = new SceneLoadData(sceneName)
            {
                ReplaceScenes = ReplaceOption.All
            };
            nm.SceneManager.LoadGlobalScenes(loadData);
        }

        public static void Disconnect()
        {
            var nm = InstanceFinder.NetworkManager;
            if (nm == null)
            {
                return;
            }

            nm.ServerManager.StopConnection(true);
            nm.ClientManager.StopConnection();
            RaiseStatus("已断开连接");
        }

        private static NetworkManager RequireNetworkManager()
        {
            var nm = InstanceFinder.NetworkManager;
            if (nm != null)
            {
                return nm;
            }

            RaiseStatus("未找到 NetworkManager。请运行 Cosmic Front → Setup All Scenes");
            Debug.LogError("[NetworkBootstrap] FishNet NetworkManager not found in scene.");
            return null;
        }

        private static void SubscribeOnce(NetworkManager nm, Action onBattleReady)
        {
            void Handler(ClientConnectionStateArgs args)
            {
                if (args.ConnectionState != LocalConnectionState.Started)
                {
                    return;
                }

                nm.ClientManager.OnClientConnectionState -= Handler;
                RaiseStatus("网络已连接，载入战场...");
                onBattleReady?.Invoke();
            }

            nm.ClientManager.OnClientConnectionState -= Handler;
            nm.ClientManager.OnClientConnectionState += Handler;
        }

        private static void RaiseStatus(string message)
        {
            StatusChanged?.Invoke(message);
            Debug.Log($"[NetworkBootstrap] {message}");
        }
    }
}
