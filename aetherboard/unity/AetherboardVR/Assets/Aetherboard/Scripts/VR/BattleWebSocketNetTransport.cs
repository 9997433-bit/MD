using System;
using UnityEngine;

namespace Aetherboard.VR
{
    public sealed class BattleWebSocketNetTransport : IBattleNetTransport
    {
        private BattleWebSocketClient _client;

        public string Name => "WebSocket";
        public bool IsConnected => _client != null && _client.IsConnected;

        public bool Connect(string host, int port, int timeoutMs = 3000)
        {
            Disconnect();
            _client = new BattleWebSocketClient();
            if (_client.Connect(host, port, timeoutMs)) return true;
            Disconnect();
            return false;
        }

        public void Disconnect()
        {
            _client?.Dispose();
            _client = null;
        }

        public void Dispose() => Disconnect();

        public bool Send(string text, bool lineDelimited) =>
            _client != null && _client.SendText(lineDelimited ? text.TrimEnd('\n') : text);

        public void StartReceiveLoop(Func<string, bool> onMessage)
        {
            _client?.RunReceiveLoop(onMessage);
        }
    }
}
