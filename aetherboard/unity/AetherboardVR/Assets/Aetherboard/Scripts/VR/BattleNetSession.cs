using System;
using Aetherboard.NetcodeIntegration;
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
        WebSocket,
        Tcp,
        NetcodeRelay
    }

    public interface IBattleNetworkBridge
    {
        bool IsAuthoritative { get; }
        bool IsHosting { get; }
        bool SubmitMove(string unitId, GridPos dest);
        bool SubmitSkill(string unitId, string skillId, GridPos? target);
        void SubmitEndPhase();
        void NotifyLocalStateChanged();
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
        [SerializeField] private bool startWsHostWhenHosting = true;
        [SerializeField] private bool enforceCoopOnNetwork = true;

        private CoopController _coop;
        private int _localPlayerId = 1;
        private IBattleNetTransport _transport;
        private Thread _readerThread;
        private volatile bool _running;
        private string _activeTransport = "—";

        public NetSessionRole Role => role;
        public bool IsAuthoritative => role != NetSessionRole.Client;
        public bool IsHosting => role == NetSessionRole.Host;
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
                NetClientTransport.Tcp => NetClientTransport.NetcodeRelay,
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
            _transport?.Dispose();
            _transport = null;
            var tcp = GetComponent<BattleTcpHostServer>();
            if (tcp != null) tcp.StopServer();
            var ws = GetComponent<BattleWebSocketHostServer>();
            if (ws != null) ws.StopServer();
            _readerThread?.Join(200);
        }

        public void SetRole(NetSessionRole newRole)
        {
            if (role == newRole) return;
            role = newRole;
            OnDestroy();
            _transport = null;
            _activeTransport = "—";
            if (role == NetSessionRole.Host) StartHost();
            else if (role == NetSessionRole.Client) ConnectClient();
        }

        private void StartHost()
        {
            if (director == null) return;
            var parts = new System.Collections.Generic.List<string>();
            if (startTcpHostWhenHosting)
            {
                var tcp = GetComponent<BattleTcpHostServer>();
                if (tcp == null) tcp = gameObject.AddComponent<BattleTcpHostServer>();
                tcp.StartServer();
                parts.Add($"TCP:{hostPort}");
            }
            if (startWsHostWhenHosting)
            {
                var ws = GetComponent<BattleWebSocketHostServer>();
                if (ws == null) ws = gameObject.AddComponent<BattleWebSocketHostServer>();
                ws.StartServer();
                parts.Add($"WS:{hostWsPort}");
            }
            _activeTransport = parts.Count > 0 ? $"Host ({string.Join(" ", parts)})" : "Host";
            Debug.Log($"[Aetherboard] Host mode — {string.Join(" | ", parts)}");
        }

        public void NotifyLocalStateChanged() => PublishHostState();

        public void PublishHostState()
        {
            if (role != NetSessionRole.Host || director == null) return;
            var line = BattleSyncProtocol.EncodeState(director.ExportSnapshotJson());
            GetComponent<BattleTcpHostServer>()?.BroadcastState(line);
            GetComponent<BattleWebSocketHostServer>()?.BroadcastState(line);
            BattleNetcodeHostCoordinator.BroadcastState(line);
        }

        private bool TryConnectTransport(BattleNetTransportKind kind, int port)
        {
            try
            {
                _transport?.Dispose();
                _transport = BattleNetTransportFactory.Create(kind);
                if (!_transport.Connect(hostAddress, port))
                {
                    _transport.Dispose();
                    _transport = null;
                    return false;
                }

                _running = true;
                _activeTransport = _transport.Name;
                _readerThread = new Thread(TransportReadLoop) { IsBackground = true };
                _readerThread.Start();
                Debug.Log($"[Aetherboard] Connected via {_transport.Name} {hostAddress}:{port}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] {kind} connect failed: {ex.Message}");
                _transport?.Dispose();
                _transport = null;
                return false;
            }
        }

        private void ConnectClient()
        {
            _activeTransport = "—";
            var connected = clientTransport switch
            {
                NetClientTransport.NetcodeRelay =>
                    TryConnectTransport(BattleNetTransportKind.NetcodeRelay, hostWsPort),
                NetClientTransport.Tcp =>
                    TryConnectTransport(BattleNetTransportKind.Tcp, hostPort),
                NetClientTransport.WebSocket =>
                    TryConnectTransport(BattleNetTransportKind.WebSocket, hostWsPort),
                _ => TryConnectTransport(BattleNetTransportKind.WebSocket, hostWsPort)
                     || TryConnectTransport(BattleNetTransportKind.Tcp, hostPort)
            };

            if (!connected)
            {
                Debug.LogWarning("[Aetherboard] Client connect failed.");
                role = NetSessionRole.Offline;
            }
        }

        private void TransportReadLoop()
        {
            _transport?.StartReceiveLoop(line =>
            {
                HandleLine(line);
                return _running;
            });
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
                PublishHostState();
                return true;
            }

            var line = BattleSyncProtocol.EncodeCommand(cmd);
            if (_transport == null || !_transport.IsConnected) return false;
            var lineDelimited = _transport.Name == "TCP";
            return _transport.Send(line, lineDelimited);
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
