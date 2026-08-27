#if AETHERBOARD_NGO_INSTALLED
using System;
using Unity.Collections;
using Unity.Netcode;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.NetcodeIntegration
{
    /// <summary>
    /// NGO CustomMessaging bridge — active when com.unity.netcode.gameobjects is installed.
    /// </summary>
    public static class BattleNetcodeFacade
    {
        private static Action<string> _onMessage;
        private static bool _registered;

        public static bool IsActive => NetworkManager.Singleton != null;

        public static bool IsServer =>
            NetworkManager.Singleton != null && NetworkManager.Singleton.IsServer;

        public static void Register(Action<string> onMessage)
        {
            _onMessage = onMessage;
            TryRegisterHandler();
            if (NetworkManager.Singleton != null)
                NetworkManager.Singleton.OnServerStarted += _ => TryRegisterHandler();
        }

        public static void Unregister()
        {
            _onMessage = null;
            _registered = false;
        }

        public static void SendToAll(string json)
        {
            if (!IsServer || string.IsNullOrEmpty(json)) return;
            var manager = NetworkManager.Singleton?.CustomMessagingManager;
            if (manager == null) return;

            var framed = BattleNetMessageCodec.Frame(json);
            var writer = new FastBufferWriter(framed.Length, Allocator.Temp);
            try
            {
                writer.WriteBytesSafe(framed, framed.Length);
                manager.SendNamedMessageToAll(
                    BattleNetcodeService.MessageName,
                    writer,
                    NetworkDelivery.ReliableFragmentedSequenced);
            }
            finally
            {
                writer.Dispose();
            }
        }

        private static void TryRegisterHandler()
        {
            if (_registered || _onMessage == null) return;
            var manager = NetworkManager.Singleton?.CustomMessagingManager;
            if (manager == null) return;

            manager.UnregisterNamedMessageHandler(BattleNetcodeService.MessageName);
            manager.RegisterNamedMessageHandler(BattleNetcodeService.MessageName, OnMessage);
            _registered = true;
        }

        private static void OnMessage(ulong senderClientId, FastBufferReader reader)
        {
            var length = reader.Length;
            if (length < BattleNetMessageCodec.HeaderSize) return;

            var bytes = new byte[length];
            reader.ReadBytesSafe(ref bytes, length);
            var json = BattleNetMessageCodec.Unframe(bytes, length);
            if (!string.IsNullOrEmpty(json))
                _onMessage?.Invoke(json);
        }
    }

    /// <summary>Shared message name — referenced from VR without NGO dependency.</summary>
    public static class BattleNetcodeService
    {
        public const string MessageName = "AetherboardBattleSync";
    }
}
#else
using System;

namespace Aetherboard.NetcodeIntegration
{
    /// <summary>Stub when Unity Netcode package is not installed.</summary>
    public static class BattleNetcodeFacade
    {
        public static bool IsActive => false;
        public static bool IsServer => false;
        public static void Register(Action<string> onMessage) { }
        public static void Unregister() { }
        public static void SendToAll(string json) { }
    }

    public static class BattleNetcodeService
    {
        public const string MessageName = "AetherboardBattleSync";
    }
}
#endif
