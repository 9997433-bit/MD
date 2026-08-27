using System;
using System.Collections.Generic;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Built-in WebSocket host — same protocol as scripts/battle_host.py (Web / Unity clients).
    /// </summary>
    public class BattleWebSocketHostServer : MonoBehaviour
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private int listenPort = 8769;
        [SerializeField] private bool enforceCoop = true;

        private CoopController _coop;
        private HttpListener _listener;
        private Thread _acceptThread;
        private volatile bool _running;
        private readonly List<WebSocket> _clients = new();
        private readonly object _clientLock = new();

        public int ListenPort => listenPort;
        public bool IsRunning => _running;

        private void Awake()
        {
            if (director == null) director = GetComponent<BattleDirector>();
            _coop = GetComponent<CoopController>();
        }

        private void OnDestroy() => StopServer();

        public void StartServer()
        {
            if (_running || director == null) return;
            try
            {
                _listener = new HttpListener();
                _listener.Prefixes.Add($"http://127.0.0.1:{listenPort}/");
                _listener.Prefixes.Add($"http://[::1]:{listenPort}/");
                _listener.Start();
                _running = true;
                _acceptThread = new Thread(AcceptLoop) { IsBackground = true };
                _acceptThread.Start();
                Debug.Log($"[Aetherboard] WebSocket Host listening on port {listenPort}");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] WebSocket Host failed to start: {ex.Message}");
                StopServer();
            }
        }

        public void StopServer()
        {
            _running = false;
            try { _listener?.Stop(); } catch { /* ignore */ }
            _listener = null;
            lock (_clientLock)
            {
                foreach (var ws in _clients)
                {
                    try { ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "", CancellationToken.None).Wait(200); }
                    catch { /* ignore */ }
                    try { ws.Dispose(); } catch { /* ignore */ }
                }
                _clients.Clear();
            }
        }

        public void BroadcastState(string stateLine) => BroadcastText(stateLine);

        private void BroadcastText(string text)
        {
            if (!_running || string.IsNullOrEmpty(text)) return;
            var bytes = Encoding.UTF8.GetBytes(text);
            List<WebSocket> dead = new();
            lock (_clientLock)
            {
                foreach (var ws in _clients)
                {
                    try
                    {
                        if (ws.State != WebSocketState.Open) { dead.Add(ws); continue; }
                        ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None)
                            .GetAwaiter()
                            .GetResult();
                    }
                    catch
                    {
                        dead.Add(ws);
                    }
                }
                foreach (var d in dead) _clients.Remove(d);
            }
        }

        private void AcceptLoop()
        {
            while (_running)
            {
                try
                {
                    var context = _listener.GetContext();
                    if (!context.Request.IsWebSocketRequest)
                    {
                        context.Response.StatusCode = 400;
                        context.Response.Close();
                        continue;
                    }

                    var wsContext = context.AcceptWebSocketAsync(null).GetAwaiter().GetResult();
                    lock (_clientLock) _clients.Add(wsContext.WebSocket);
                    var thread = new Thread(() => ClientLoop(wsContext.WebSocket)) { IsBackground = true };
                    thread.Start();
                }
                catch (HttpListenerException)
                {
                    if (!_running) break;
                }
                catch (ObjectDisposedException)
                {
                    break;
                }
            }
        }

        private void ClientLoop(WebSocket ws)
        {
            try
            {
                var coopOn = enforceCoop && _coop != null && _coop.Mode == CoopMode.SplitCoop;
                SendText(ws, BattleSyncProtocol.EncodeWelcome(
                    director.Engine.RandomSeed, director.Engine.BossId, coopOn));
                SendText(ws, BattleSyncProtocol.EncodeState(director.ExportSnapshotJson()));

                var buffer = new byte[8192];
                var builder = new StringBuilder(256);
                while (_running && ws.State == WebSocketState.Open)
                {
                    builder.Clear();
                    WebSocketReceiveResult result;
                    do
                    {
                        result = ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None)
                            .GetAwaiter()
                            .GetResult();
                        if (result.MessageType == WebSocketMessageType.Close) return;
                        builder.Append(Encoding.UTF8.GetString(buffer, 0, result.Count));
                    } while (!result.EndOfMessage);

                    var line = builder.ToString();
                    if (string.IsNullOrWhiteSpace(line)) continue;

                    var cmd = BattleSyncProtocol.ExtractCommand(line);
                    if (cmd == null)
                    {
                        SendText(ws, BattleSyncProtocol.EncodeError("Invalid command"));
                        continue;
                    }

                    if (coopOn && CoopRules.CommandRequiresUnit(cmd.Type) &&
                        !CoopRules.CanControl(cmd.PlayerId, cmd.UnitId, true))
                    {
                        SendText(ws, BattleSyncProtocol.EncodeError($"P{cmd.PlayerId} 无权控制 {cmd.UnitId}"));
                        continue;
                    }

                    var ok = BattleCommandExecutor.Apply(director.Engine, cmd);
                    var stateJson = director.ExportSnapshotJson();
                    if (!ok)
                    {
                        SendText(ws, BattleSyncProtocol.EncodeError("Command rejected"));
                        continue;
                    }

                    UnityMainThreadDispatcher.Enqueue(() => director.RefreshAllViews());
                    var stateLine = BattleSyncProtocol.EncodeState(stateJson);
                    BroadcastText(stateLine);
                }
            }
            catch (WebSocketException)
            {
                // client disconnected
            }
            finally
            {
                lock (_clientLock) _clients.Remove(ws);
                try { ws.Dispose(); } catch { /* ignore */ }
            }
        }

        private static void SendText(WebSocket ws, string text)
        {
            if (ws.State != WebSocketState.Open) return;
            var bytes = Encoding.UTF8.GetBytes(text);
            ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None)
                .GetAwaiter()
                .GetResult();
        }
    }
}
