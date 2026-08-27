using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;

namespace Aetherboard.VR
{
    /// <summary>
    /// Minimal WebSocket text client for Python host (port 8769).
    /// </summary>
    public sealed class BattleWebSocketClient : IDisposable
    {
        private ClientWebSocket _socket;
        private CancellationTokenSource _cts;
        private readonly object _sendLock = new();

        public bool IsConnected => _socket?.State == WebSocketState.Open;

        public bool Connect(string host, int port, int timeoutMs = 3000)
        {
            Disconnect();
            _cts = new CancellationTokenSource();
            _socket = new ClientWebSocket();
            var uri = new Uri($"ws://{host}:{port}");

            try
            {
                var task = _socket.ConnectAsync(uri, _cts.Token);
                if (!task.Wait(timeoutMs))
                {
                    Disconnect();
                    return false;
                }
                return _socket.State == WebSocketState.Open;
            }
            catch
            {
                Disconnect();
                return false;
            }
        }

        public void Disconnect()
        {
            try { _cts?.Cancel(); } catch { /* ignore */ }
            if (_socket != null)
            {
                try
                {
                    if (_socket.State is WebSocketState.Open or WebSocketState.CloseReceived)
                        _socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "", CancellationToken.None)
                            .Wait(500);
                }
                catch { /* ignore */ }
                _socket.Dispose();
            }
            _socket = null;
            _cts?.Dispose();
            _cts = null;
        }

        public void Dispose() => Disconnect();

        public bool SendText(string text)
        {
            if (!IsConnected) return false;
            var bytes = Encoding.UTF8.GetBytes(text);
            lock (_sendLock)
            {
                try
                {
                    _socket.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, _cts.Token)
                        .GetAwaiter()
                        .GetResult();
                    return true;
                }
                catch
                {
                    return false;
                }
            }
        }

        public void RunReceiveLoop(Func<string, bool> onMessage)
        {
            var buffer = new byte[8192];
            var builder = new StringBuilder(256);
            while (IsConnected && _cts is { IsCancellationRequested: false })
            {
                try
                {
                    builder.Clear();
                    WebSocketReceiveResult result;
                    do
                    {
                        result = _socket.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token)
                            .GetAwaiter()
                            .GetResult();
                        if (result.MessageType == WebSocketMessageType.Close) return;
                        builder.Append(Encoding.UTF8.GetString(buffer, 0, result.Count));
                    } while (!result.EndOfMessage);

                    var msg = builder.ToString();
                    if (!string.IsNullOrWhiteSpace(msg) && !onMessage(msg))
                        return;
                }
                catch (OperationCanceledException)
                {
                    return;
                }
                catch (Exception ex)
                {
                    if (_cts is { IsCancellationRequested: false })
                        UnityEngine.Debug.LogWarning($"[Aetherboard] WebSocket reader stopped: {ex.Message}");
                    return;
                }
            }
        }
    }
}
