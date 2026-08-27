using System;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public enum NetSessionRole
    {
        Offline,
        Host,
        Client
    }

    public enum NetClientTransport
    {
        Auto,
        Tcp,
        WebSocket
    }

    public interface IBattleNetworkBridge
    {
        bool IsAuthoritative { get; }
        bool SubmitMove(string unitId, GridPos dest);
        bool SubmitSkill(string unitId, string skillId, GridPos? target);
        void SubmitEndPhase();
    }

    /// <summary>
    /// Offline / Host / Client battle sync. Host is authoritative; clients send commands.
    /// Client supports WebSocket (8769) with TCP (8767) fallback.
    /// </summary>
    public class BattleNetSession : MonoBehaviour, IBattleNetworkBridge
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private NetSessionRole role = NetSessionRole.Offline;
        [SerializeField] private string hostAddress = "127.0.0.1";
        [SerializeField] private int hostPort = 8767;
        [SerializeField] private int hostWsPort = 8769;
        [SerializeField] private NetClientTransport clientTransport = NetClientTransport.Auto;
        [SerializeField] private bool startTcpHostWhenHosting = true;
        [SerializeField] private bool enforceCoopOnNetwork = true;

        private CoopController _coop;
        private int _localPlayerId = 1;
        private TcpClient _client;
        private BattleWebSocketClient _wsClient;
        private Thread _readerThread;
        private volatile bool _running;
        private readonly object _sendLock = new();
        private string _activeTransport = "—";

        public NetSessionRole Role => role;
        public bool IsAuthoritative => role != NetSessionRole.Client;
        public string HostAddress => hostAddress;
        public int HostPort => hostPort;
        public int HostWsPort => hostWsPort;
        public NetClientTransport ClientTransport => clientTransport;
        public string ActiveTransport => _activeTransport;

        private void Awake()
        {
            if (director == null) director = GetComponent<BattleDirector>();
            _coop = GetComponent<CoopController>();
            director?.SetNetworkBridge(this);
        }

        public int LocalPlayerId => _localPlayerId;

        public void SetLocalPlayerId(int playerId)
        {
            _localPlayerId = playerId == 2 ? 2 : 1;
        }

        public void CycleClientTransport()
        {
            clientTransport = clientTransport switch
            {
                NetClientTransport.Auto => NetClientTransport.WebSocket,
                NetClientTransport.WebSocket => NetClientTransport.Tcp,
                _ => NetClientTransport.Auto
            };
            Debug.Log($"[Aetherboard] Client transport → {clientTransport}");
        }

        private void Start()
        {
            if (role == NetSessionRole.Host)
                StartHost();
            else if (role == NetSessionRole.Client)
                ConnectClient();
        }

        private void OnDestroy()
        {
            _running = false;
            try { _client?.Close(); } catch { /* ignore */ }
            _wsClient?.Dispose();
            _wsClient = null;
            var tcp = GetComponent<BattleTcpHostServer>();
            if (tcp != null) tcp.StopServer();
            _readerThread?.Join(200);
        }

        public void SetRole(NetSessionRole newRole)
        {
            if (role == newRole) return;
            role = newRole;
            OnDestroy();
            _client = null;
            _wsClient = null;
            _activeTransport = "—";
            if (role == NetSessionRole.Host) StartHost();
            else if (role == NetSessionRole.Client) ConnectClient();
        }

        private void StartHost()
        {
            if (director == null) return;
            _activeTransport = "TCP Host";
            if (startTcpHostWhenHosting)
            {
                var tcp = GetComponent<BattleTcpHostServer>();
                if (tcp == null) tcp = gameObject.AddComponent<BattleTcpHostServer>();
                tcp.StartServer();
            }
            Debug.Log($"[Aetherboard] Host mode — TCP :{hostPort} | Python WS :{hostWsPort} for Web/Unity");
        }

        private void ConnectClient()
        {
            _activeTransport = "—";
            var connected = false;

            if (clientTransport != NetClientTransport.Tcp)
                connected = TryConnectWebSocket();

            if (!connected && clientTransport != NetClientTransport.WebSocket)
                connected = TryConnectTcp();

            if (!connected)
            {
                Debug.LogWarning("[Aetherboard] Client connect failed (tried WS/TCP per transport setting).");
                role = NetSessionRole.Offline;
            }
        }

        private bool TryConnectWebSocket()
        {
            try
            {
                _wsClient = new BattleWebSocketClient();
                if (!_wsClient.Connect(hostAddress, hostWsPort))
                {
                    _wsClient.Dispose();
                    _wsClient = null;
                    return false;
                }

                _running = true;
                _activeTransport = "WebSocket";
                _readerThread = new Thread(WsReadLoop) { IsBackground = true };
                _readerThread.Start();
                Debug.Log($"[Aetherboard] Connected via WebSocket {hostAddress}:{hostWsPort}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] WebSocket connect failed: {ex.Message}");
                _wsClient?.Dispose();
                _wsClient = null;
                return false;
            }
        }

        private bool TryConnectTcp()
        {
            try
            {
                _client = new TcpClient(hostAddress, hostPort);
                _running = true;
                _activeTransport = "TCP";
                _readerThread = new Thread(TcpReadLoop) { IsBackground = true };
                _readerThread.Start();
                Debug.Log($"[Aetherboard] Connected via TCP {hostAddress}:{hostPort}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] TCP connect failed: {ex.Message}");
                return false;
            }
        }

        public bool SubmitMove(string unitId, GridPos dest) =>
            SubmitCommand(new BattleCommand
            {
                Type = BattleCommandType.Move,
                UnitId = unitId,
                TargetX = dest.X,
                TargetY = dest.Y
            });

        public bool SubmitSkill(string unitId, string skillId, GridPos? target) =>
            SubmitCommand(new BattleCommand
            {
                Type = BattleCommandType.Skill,
                UnitId = unitId,
                SkillId = skillId,
                TargetX = target?.X ?? -1,
                TargetY = target?.Y ?? -1
            });

        public void SubmitEndPhase() =>
            SubmitCommand(new BattleCommand { Type = BattleCommandType.EndPhase });

        private bool SubmitCommand(BattleCommand cmd)
        {
            if (role == NetSessionRole.Offline) return false;

            var coopActive = enforceCoopOnNetwork && _coop != null && _coop.Mode == CoopMode.SplitCoop;
            cmd.PlayerId = coopActive ? _localPlayerId : 0;

            if (coopActive && CoopRules.CommandRequiresUnit(cmd.Type) &&
                !CoopRules.CanControl(cmd.PlayerId, cmd.UnitId, true))
            {
                Debug.LogWarning($"[Aetherboard] P{cmd.PlayerId} 无权控制 {cmd.UnitId}");
                return false;
            }

            if (role == NetSessionRole.Host)
            {
                if (director == null) return false;
                var ok = BattleCommandExecutor.Apply(director.Engine, cmd);
                if (!ok)
                {
                    Debug.LogWarning("[Aetherboard] Host rejected command.");
                    return false;
                }
                director.RefreshAllViews();
                return true;
            }

            var line = BattleSyncProtocol.EncodeCommand(cmd);
            if (_wsClient != null && _wsClient.IsConnected)
                return _wsClient.SendText(line);

            if (_client == null || !_client.Connected) return false;
            try
            {
                var bytes = Encoding.UTF8.GetBytes(line + "\n");
                lock (_sendLock)
                    _client.GetStream().Write(bytes, 0, bytes.Length);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] Send failed: {ex.Message}");
                return false;
            }
        }

        private void WsReadLoop()
        {
            _wsClient?.RunReceiveLoop(line =>
            {
                HandleLine(line);
                return _running;
            });
        }

        private void TcpReadLoop()
        {
            try
            {
                using var stream = _client.GetStream();
                using var reader = new StreamReader(stream, Encoding.UTF8);
                while (_running && _client.Connected)
                {
                    var line = reader.ReadLine();
                    if (line == null) break;
                    HandleLine(line);
                }
            }
            catch (Exception ex)
            {
                if (_running) Debug.LogWarning($"[Aetherboard] Reader stopped: {ex.Message}");
            }
        }

        private void HandleLine(string line)
        {
            var type = BattleSyncProtocol.ExtractType(line);
            if (type == BattleSyncProtocol.TypeWelcome)
            {
                var welcome = BattleSyncProtocol.ParseWelcome(line);
                if (welcome != null && welcome.Coop && _coop != null)
                    UnityMainThreadDispatcher.Enqueue(() => _coop.SetNetworkCoop(true));
            }
            else if (type == BattleSyncProtocol.TypeState)
            {
                var payload = BattleSyncProtocol.ExtractStatePayload(line);
                if (payload != null)
                    UnityMainThreadDispatcher.Enqueue(() => director?.ImportSnapshotJson(payload));
            }
            else if (type == BattleSyncProtocol.TypeError)
            {
                var message = BattleSyncProtocol.ExtractErrorMessage(line);
                Debug.LogWarning($"[Aetherboard] Server error: {message}");
            }
        }

        public string HostPublishState() => director?.ExportSnapshotJson();

        public bool ClientApplyState(string json) => director != null && director.ImportSnapshotJson(json);

        public string ExportCommandLog() => director?.CommandLog.ToJson();
    }

    /// <summary>
    /// Minimal main-thread queue for TCP reader callbacks.
    /// </summary>
    internal static class UnityMainThreadDispatcher
    {
        private static readonly System.Collections.Generic.Queue<Action> Queue = new();
        private static bool _initialized;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Init()
        {
            if (_initialized) return;
            _initialized = true;
            var go = new GameObject("MainThreadDispatcher");
            go.hideFlags = HideFlags.HideAndDontSave;
            go.AddComponent<DispatcherBehaviour>();
        }

        public static void Enqueue(Action action)
        {
            lock (Queue) Queue.Enqueue(action);
        }

        private class DispatcherBehaviour : MonoBehaviour
        {
            private void Update()
            {
                while (true)
                {
                    Action action;
                    lock (Queue)
                    {
                        if (Queue.Count == 0) break;
                        action = Queue.Dequeue();
                    }
                    action?.Invoke();
                }
            }
        }
    }
}
