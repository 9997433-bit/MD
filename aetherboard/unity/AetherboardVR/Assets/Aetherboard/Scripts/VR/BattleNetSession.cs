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

    public interface IBattleNetworkBridge
    {
        bool IsAuthoritative { get; }
        bool SubmitMove(string unitId, GridPos dest);
        bool SubmitSkill(string unitId, string skillId, GridPos? target);
        void SubmitEndPhase();
    }

    /// <summary>
    /// Offline / Host / Client battle sync. Host is authoritative; clients send commands.
    /// </summary>
    public class BattleNetSession : MonoBehaviour, IBattleNetworkBridge
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private NetSessionRole role = NetSessionRole.Offline;
        [SerializeField] private string hostAddress = "127.0.0.1";
        [SerializeField] private int hostPort = 8767;
        [SerializeField] private bool startTcpHostWhenHosting = true;

        private TcpClient _client;
        private Thread _readerThread;
        private volatile bool _running;
        private readonly object _sendLock = new();

        public NetSessionRole Role => role;
        public bool IsAuthoritative => role != NetSessionRole.Client;
        public string HostAddress => hostAddress;
        public int HostPort => hostPort;

        private void Awake()
        {
            if (director == null) director = GetComponent<BattleDirector>();
            director?.SetNetworkBridge(this);
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
            if (role == NetSessionRole.Host) StartHost();
            else if (role == NetSessionRole.Client) ConnectClient();
        }

        private void StartHost()
        {
            if (director == null) return;
            if (startTcpHostWhenHosting)
            {
                var tcp = GetComponent<BattleTcpHostServer>();
                if (tcp == null) tcp = gameObject.AddComponent<BattleTcpHostServer>();
                tcp.StartServer();
            }
            Debug.Log($"[Aetherboard] Host mode — TCP :{hostPort} | Python HTTP :8768 for Web");
        }

        private void ConnectClient()
        {
            try
            {
                _client = new TcpClient(hostAddress, hostPort);
                _running = true;
                _readerThread = new Thread(ReadLoop) { IsBackground = true };
                _readerThread.Start();
                Debug.Log($"[Aetherboard] Connected to {hostAddress}:{hostPort}");
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] Client connect failed: {ex.Message}");
                role = NetSessionRole.Offline;
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

            if (_client == null || !_client.Connected) return false;
            try
            {
                var line = BattleSyncProtocol.EncodeCommand(cmd) + "\n";
                var bytes = Encoding.UTF8.GetBytes(line);
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

        private void ReadLoop()
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
            if (type == BattleSyncProtocol.TypeState)
            {
                var payload = BattleSyncProtocol.ExtractStatePayload(line);
                if (payload != null)
                    UnityMainThreadDispatcher.Enqueue(() => director?.ImportSnapshotJson(payload));
            }
            else if (type == BattleSyncProtocol.TypeError)
            {
                Debug.LogWarning($"[Aetherboard] Server error: {line}");
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
