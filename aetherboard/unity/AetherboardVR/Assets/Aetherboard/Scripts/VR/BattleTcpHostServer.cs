using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Built-in TCP host server — same protocol as scripts/battle_host.py (Unity / LAN clients).
    /// </summary>
    public class BattleTcpHostServer : MonoBehaviour
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private int listenPort = 8767;
        [SerializeField] private bool startOnAwake = false;

        [SerializeField] private bool enforceCoop = true;

        private CoopController _coop;
        private TcpListener _listener;
        private Thread _acceptThread;
        private volatile bool _running;
        private readonly List<TcpClient> _clients = new();
        private readonly object _clientLock = new();

        private void Awake()
        {
            if (director == null) director = GetComponent<BattleDirector>();
            _coop = GetComponent<CoopController>();
        }

        private void Start()
        {
            if (startOnAwake) StartServer();
        }

        private void OnDestroy() => StopServer();

        public void StartServer()
        {
            if (_running || director == null) return;
            _running = true;
            _listener = new TcpListener(IPAddress.Any, listenPort);
            _listener.Start();
            _acceptThread = new Thread(AcceptLoop) { IsBackground = true };
            _acceptThread.Start();
            Debug.Log($"[Aetherboard] TCP Host listening on port {listenPort}");
        }

        public void StopServer()
        {
            _running = false;
            try { _listener?.Stop(); } catch { /* ignore */ }
            lock (_clientLock)
            {
                foreach (var c in _clients)
                    try { c.Close(); } catch { /* ignore */ }
                _clients.Clear();
            }
        }

        private void AcceptLoop()
        {
            while (_running)
            {
                try
                {
                    var client = _listener.AcceptTcpClient();
                    lock (_clientLock) _clients.Add(client);
                    var thread = new Thread(() => ClientLoop(client)) { IsBackground = true };
                    thread.Start();
                }
                catch (SocketException)
                {
                    if (!_running) break;
                }
            }
        }

        private void ClientLoop(TcpClient client)
        {
            try
            {
                using var stream = client.GetStream();
                using var reader = new StreamReader(stream, Encoding.UTF8);
                var writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true };

                writer.WriteLine(BattleSyncProtocol.EncodeWelcome(
                    director.Engine.RandomSeed, director.Engine.BossId,
                    enforceCoop && _coop != null && _coop.Mode == CoopMode.SplitCoop));
                writer.WriteLine(BattleSyncProtocol.EncodeState(director.ExportSnapshotJson()));

                string line;
                while (_running && client.Connected && (line = reader.ReadLine()) != null)
                {
                    if (string.IsNullOrWhiteSpace(line)) continue;
                    var cmd = BattleSyncProtocol.ExtractCommand(line);
                    if (cmd == null)
                    {
                        writer.WriteLine(BattleSyncProtocol.EncodeError("Invalid command"));
                        continue;
                    }

                    var coopOn = enforceCoop && _coop != null && _coop.Mode == CoopMode.SplitCoop;
                    if (coopOn && CoopRules.CommandRequiresUnit(cmd.Type) &&
                        !CoopRules.CanControl(cmd.PlayerId, cmd.UnitId, true))
                    {
                        writer.WriteLine(BattleSyncProtocol.EncodeError($"P{cmd.PlayerId} 无权控制 {cmd.UnitId}"));
                        continue;
                    }

                    var ok = BattleCommandExecutor.Apply(director.Engine, cmd);
                    var stateJson = director.ExportSnapshotJson();
                    if (!ok)
                    {
                        writer.WriteLine(BattleSyncProtocol.EncodeError("Command rejected"));
                        continue;
                    }

                    UnityMainThreadDispatcher.Enqueue(() => director.RefreshAllViews());
                    var stateLine = BattleSyncProtocol.EncodeState(stateJson);
                    Broadcast(stateLine);
                }
            }
            catch (IOException)
            {
                // client disconnected
            }
            finally
            {
                lock (_clientLock) _clients.Remove(client);
                try { client.Close(); } catch { /* ignore */ }
            }
        }

        private void Broadcast(string line)
        {
            BroadcastState(line);
        }

        public void BroadcastState(string line)
        {
            var bytes = Encoding.UTF8.GetBytes(line + "\n");
            List<TcpClient> dead = new();
            lock (_clientLock)
            {
                foreach (var client in _clients)
                {
                    try
                    {
                        if (!client.Connected) { dead.Add(client); continue; }
                        client.GetStream().Write(bytes, 0, bytes.Length);
                    }
                    catch
                    {
                        dead.Add(client);
                    }
                }
                foreach (var d in dead) _clients.Remove(d);
            }
        }
    }
}
