using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

namespace Aetherboard.VR
{
    public sealed class BattleTcpNetTransport : IBattleNetTransport
    {
        private TcpClient _client;
        private readonly object _sendLock = new();

        public string Name => "TCP";
        public bool IsConnected => _client != null && _client.Connected;

        public bool Connect(string host, int port, int timeoutMs = 3000)
        {
            Disconnect();
            try
            {
                _client = new TcpClient();
                var result = _client.BeginConnect(host, port, null, null);
                if (!result.AsyncWaitHandle.WaitOne(timeoutMs))
                {
                    Disconnect();
                    return false;
                }
                _client.EndConnect(result);
                return _client.Connected;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] TCP transport connect failed: {ex.Message}");
                Disconnect();
                return false;
            }
        }

        public void Disconnect()
        {
            try { _client?.Close(); } catch { /* ignore */ }
            _client = null;
        }

        public void Dispose() => Disconnect();

        public bool Send(string text, bool lineDelimited)
        {
            if (!IsConnected) return false;
            try
            {
                var payload = lineDelimited ? text + "\n" : text;
                var bytes = Encoding.UTF8.GetBytes(payload);
                lock (_sendLock)
                    _client.GetStream().Write(bytes, 0, bytes.Length);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] TCP send failed: {ex.Message}");
                return false;
            }
        }

        public void StartReceiveLoop(Func<string, bool> onMessage)
        {
            if (!IsConnected) return;
            try
            {
                using var stream = _client.GetStream();
                using var reader = new StreamReader(stream, Encoding.UTF8);
                while (IsConnected)
                {
                    var line = reader.ReadLine();
                    if (line == null) break;
                    if (!string.IsNullOrWhiteSpace(line) && !onMessage(line))
                        break;
                }
            }
            catch (Exception ex)
            {
                if (IsConnected) Debug.LogWarning($"[Aetherboard] TCP reader stopped: {ex.Message}");
            }
        }
    }
}
