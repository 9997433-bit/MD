using System;
using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Netcode-ready transport: uses framed messages via WebSocket relay until NGO transport ships.
    /// </summary>
    public sealed class BattleNetcodeRelayTransport : IBattleNetTransport
    {
        private readonly BattleWebSocketNetTransport _inner = new();

        public string Name => BattleNetcodeRuntime.IsAvailable ? "Netcode-Relay" : "Netcode-Relay→WS";
        public bool IsConnected => _inner.IsConnected;

        public bool Connect(string host, int port, int timeoutMs = 3000)
        {
            BattleNetcodeRuntime.LogStatus();
            var ok = _inner.Connect(host, port, timeoutMs);
            if (ok)
                EnsureNetcodeService();
            return ok;
        }

        public void Disconnect() => _inner.Disconnect();

        public void Dispose() => _inner.Dispose();

        public bool Send(string text, bool lineDelimited)
        {
            // Wire format stays JSON text for Python / Unity WS hosts.
            // BattleNetMessageCodec.Frame is used when publishing through BattleNetcodeService.
            BattleNetcodeService.Instance?.PublishBattleMessage(text);
            return _inner.Send(text, lineDelimited);
        }

        public void StartReceiveLoop(Func<string, bool> onMessage)
        {
            _inner.StartReceiveLoop(line =>
            {
                BattleNetcodeService.Instance?.ReceiveBattleMessage(line);
                return onMessage(line);
            });
        }

        private static void EnsureNetcodeService()
        {
            if (BattleNetcodeService.Instance != null) return;
            var go = new GameObject("BattleNetcodeService");
            go.AddComponent<BattleNetcodeService>();
        }
    }
}
