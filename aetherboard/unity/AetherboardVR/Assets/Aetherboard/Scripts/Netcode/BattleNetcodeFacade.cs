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
        private static Action<string> _onSyncMessage;
        private static Action<string, ulong> _onCommandMessage;
        private static bool _syncRegistered;
        private static bool _commandRegistered;

        public static bool IsActive => NetworkManager.Singleton != null;

        public static bool IsServer =>
            NetworkManager.Singleton != null && NetworkManager.Singleton.IsServer;

        public static bool IsClient =>
            NetworkManager.Singleton != null && NetworkManager.Singleton.IsClient;

        public static void RegisterSync(Action<string> onMessage)
        {
            _onSyncMessage = onMessage;
            TryRegisterSyncHandler();
            if (NetworkManager.Singleton != null)
                NetworkManager.Singleton.OnServerStarted += _ => TryRegisterSyncHandler();
        }

        public static void RegisterCommandHandler(Action<string, ulong> onCommand)
        {
            _onCommandMessage = onCommand;
            TryRegisterCommandHandler();
            if (NetworkManager.Singleton != null)
                NetworkManager.Singleton.OnServerStarted += _ => TryRegisterCommandHandler();
        }

        public static void Unregister()
        {
            _onSyncMessage = null;
            _onCommandMessage = null;
            _syncRegistered = false;
            _commandRegistered = false;
        }

        public static void SendToAll(string json) =>
            SendNamed(BattleNetcodeService.SyncMessageName, json, NetworkDelivery.ReliableFragmentedSequenced, null);

        public static void SendToClient(ulong clientId, string json) =>
            SendNamed(BattleNetcodeService.SyncMessageName, json, NetworkDelivery.ReliableFragmentedSequenced, clientId);

        public static void SendToServer(string json)
        {
            if (string.IsNullOrEmpty(json)) return;
            var manager = NetworkManager.Singleton?.CustomMessagingManager;
            if (manager == null || !IsClient) return;

            var framed = BattleNetMessageCodec.Frame(json);
            var writer = new FastBufferWriter(framed.Length, Allocator.Temp);
            try
            {
                writer.WriteBytesSafe(framed, framed.Length);
                manager.SendNamedMessage(
                    BattleNetcodeService.CommandMessageName,
                    NetworkManager.ServerClientId,
                    writer,
                    NetworkDelivery.ReliableFragmentedSequenced);
            }
            finally
            {
                writer.Dispose();
            }
        }

        private static void SendNamed(string messageName, string json, NetworkDelivery delivery, ulong? clientId)
        {
            if (!IsServer || string.IsNullOrEmpty(json)) return;
            var manager = NetworkManager.Singleton?.CustomMessagingManager;
            if (manager == null) return;

            var framed = BattleNetMessageCodec.Frame(json);
            var writer = new FastBufferWriter(framed.Length, Allocator.Temp);
            try
            {
                writer.WriteBytesSafe(framed, framed.Length);
                if (clientId.HasValue)
                    manager.SendNamedMessage(messageName, clientId.Value, writer, delivery);
                else
                    manager.SendNamedMessageToAll(messageName, writer, delivery);
            }
            finally
            {
                writer.Dispose();
            }
        }

        private static void TryRegisterSyncHandler()
        {
            if (_syncRegistered || _onSyncMessage == null) return;
            var manager = NetworkManager.Singleton?.CustomMessagingManager;
            if (manager == null) return;

            manager.UnregisterNamedMessageHandler(BattleNetcodeService.SyncMessageName);
            manager.RegisterNamedMessageHandler(BattleNetcodeService.SyncMessageName, OnSyncMessage);
            _syncRegistered = true;
        }

        private static void TryRegisterCommandHandler()
        {
            if (_commandRegistered || _onCommandMessage == null) return;
            var manager = NetworkManager.Singleton?.CustomMessagingManager;
            if (manager == null || !IsServer) return;

            manager.UnregisterNamedMessageHandler(BattleNetcodeService.CommandMessageName);
            manager.RegisterNamedMessageHandler(BattleNetcodeService.CommandMessageName, OnCommandMessage);
            _commandRegistered = true;
        }

        private static void OnSyncMessage(ulong senderClientId, FastBufferReader reader)
        {
            var json = ReadFramedJson(reader);
            if (!string.IsNullOrEmpty(json))
                _onSyncMessage?.Invoke(json);
        }

        private static void OnCommandMessage(ulong senderClientId, FastBufferReader reader)
        {
            var json = ReadFramedJson(reader);
            if (!string.IsNullOrEmpty(json))
                _onCommandMessage?.Invoke(json, senderClientId);
        }

        private static string ReadFramedJson(FastBufferReader reader)
        {
            var length = reader.Length;
            if (length < BattleNetMessageCodec.HeaderSize) return null;

            var bytes = new byte[length];
            reader.ReadBytesSafe(ref bytes, length);
            return BattleNetMessageCodec.Unframe(bytes, length);
        }
    }

    /// <summary>Shared message names — referenced from VR without direct NGO types.</summary>
    public static class BattleNetcodeService
    {
        public const string SyncMessageName = "AetherboardBattleSync";
        public const string CommandMessageName = "AetherboardBattleCommand";
        public const string MessageName = SyncMessageName;
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
        public static bool IsClient => false;
        public static void RegisterSync(Action<string> onMessage) { }
        public static void RegisterCommandHandler(Action<string, ulong> onCommand) { }
        public static void Unregister() { }
        public static void SendToAll(string json) { }
        public static void SendToClient(ulong clientId, string json) { }
        public static void SendToServer(string json) { }
    }

    public static class BattleNetcodeService
    {
        public const string SyncMessageName = "AetherboardBattleSync";
        public const string CommandMessageName = "AetherboardBattleCommand";
        public const string MessageName = SyncMessageName;
    }
}
#endif
