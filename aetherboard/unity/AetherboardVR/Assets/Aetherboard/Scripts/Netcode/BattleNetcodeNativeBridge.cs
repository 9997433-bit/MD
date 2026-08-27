#if AETHERBOARD_NGO_INSTALLED
using System;
using System.Threading;
using Unity.Netcode;
using Unity.Netcode.Transports.UTP;
using UnityEngine;

namespace Aetherboard.NetcodeIntegration
{
    /// <summary>
    /// Runtime NetworkManager + UnityTransport bootstrap for native NGO battle sync.
    /// </summary>
    public static class BattleNetcodeNativeBridge
    {
        private static NetworkManager _manager;
        private static UnityTransport _transport;
        private static Action<string> _onLine;

        public static bool IsConnected =>
            _manager != null && (_manager.IsClient || _manager.IsServer);

        public static bool IsClient => _manager != null && _manager.IsConnectedClient;
        public static bool IsServer => _manager != null && _manager.IsServer;

        public static event Action<string> OnLineReceived
        {
            add
            {
                _onLine += value;
                BattleNetcodeFacade.RegisterSync(DispatchLine);
            }
            remove
            {
                _onLine -= value;
                if (_onLine == null)
                    BattleNetcodeFacade.Unregister();
            }
        }

        public static bool StartHost(string address, int port, int timeoutMs = 5000)
        {
            if (!EnsureNetworkManager()) return false;
            ConfigureTransport(address, port);

            if (_manager.IsServer || _manager.IsClient)
                _manager.Shutdown();

            if (!_manager.StartHost())
            {
                Debug.LogWarning("[Aetherboard] NGO StartHost failed.");
                return false;
            }

            return WaitFor(() => _manager.IsServer, timeoutMs);
        }

        public static bool ConnectClient(string address, int port, int timeoutMs = 5000)
        {
            if (!EnsureNetworkManager()) return false;
            ConfigureTransport(address, port);

            if (_manager.IsServer || _manager.IsClient)
                _manager.Shutdown();

            if (!_manager.StartClient())
            {
                Debug.LogWarning("[Aetherboard] NGO StartClient failed.");
                return false;
            }

            return WaitFor(() => _manager.IsConnectedClient, timeoutMs);
        }

        public static bool SendCommand(string json)
        {
            if (string.IsNullOrEmpty(json) || !IsClient) return false;
            BattleNetcodeFacade.SendToServer(json);
            return true;
        }

        public static void Shutdown()
        {
            if (_manager == null) return;
            try
            {
                if (_manager.IsServer || _manager.IsClient)
                    _manager.Shutdown();
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] NGO shutdown: {ex.Message}");
            }
        }

        private static void DispatchLine(string json) => _onLine?.Invoke(json);

        private static bool EnsureNetworkManager()
        {
            if (_manager != null) return true;

            var existing = UnityEngine.Object.FindObjectOfType<NetworkManager>();
            if (existing != null)
            {
                _manager = existing;
                _transport = existing.GetComponent<UnityTransport>();
                if (_transport == null)
                    _transport = existing.gameObject.AddComponent<UnityTransport>();
                return true;
            }

            var go = new GameObject("AetherboardNetworkManager");
            UnityEngine.Object.DontDestroyOnLoad(go);
            _transport = go.AddComponent<UnityTransport>();
            _manager = go.AddComponent<NetworkManager>();
            return _manager != null;
        }

        private static void ConfigureTransport(string address, int port)
        {
            if (_transport == null) return;
            var listenAddress = string.IsNullOrWhiteSpace(address) ? "127.0.0.1" : address.Trim();
            _transport.SetConnectionData(listenAddress, (ushort)Mathf.Clamp(port, 1, 65535));
        }

        private static bool WaitFor(Func<bool> predicate, int timeoutMs)
        {
            var deadline = Environment.TickCount + timeoutMs;
            while (Environment.TickCount < deadline)
            {
                if (predicate()) return true;
                Thread.Sleep(50);
            }
            return predicate();
        }
    }
}
#else
namespace Aetherboard.NetcodeIntegration
{
  public static class BattleNetcodeNativeBridge
  {
    public static bool IsConnected => false;
    public static bool IsClient => false;
    public static bool IsServer => false;
    public static event System.Action<string> OnLineReceived;
    public static bool StartHost(string address, int port, int timeoutMs = 5000) => false;
    public static bool ConnectClient(string address, int port, int timeoutMs = 5000) => false;
    public static bool SendCommand(string json) => false;
    public static void Shutdown() { }
  }
}
#endif
