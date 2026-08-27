using System;
using System.IO;
using UnityEngine;
using UnityEngine.Events;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Central orchestrator: owns BattleEngine, drives table view and VFX.
    /// Attach to a scene root object.
    /// </summary>
    public class BattleDirector : MonoBehaviour
    {
        [Header("Battle")]
        [SerializeField] private string bossId = "earth";
        [SerializeField] private int randomSeed = 42;

        [Header("References")]
        [SerializeField] private BattleTableView tableView;
        [SerializeField] private TelegraphVFXController telegraphVfx;
        [SerializeField] private BossHologramView bossView;

        public BattleEngine Engine { get; private set; }
        public BattleState State => Engine.State;

        public UnityEvent<BattlePhase> OnPhaseChanged = new();
        public UnityEvent<string> OnLogAdded = new();
        public UnityEvent OnBattleEnded = new();
        public UnityEvent OnCastInterrupted = new();
        public UnityEvent<string> OnBossChanged = new();

        public BattleCommandLog CommandLog { get; } = new();
        private string _lastSnapshotJson;
        private IBattleNetworkBridge _network;

        public void SetNetworkBridge(IBattleNetworkBridge bridge) => _network = bridge;

        private void Awake()
        {
            bossId = BattleBossPrefs.LoadBoss(bossId);
            Engine = new BattleEngine(bossId, randomSeed);
            CommandLog.RandomSeed = randomSeed;
            CommandLog.BossId = bossId;
            Engine.BeginWarning();
        }

        private void Start()
        {
            RefreshAllViews();
        }

        public void SetBoss(string id)
        {
            bossId = id;
            BattleBossPrefs.SaveBoss(bossId);
            Engine.Reset(randomSeed, bossId);
            CommandLog.BossId = bossId;
            CommandLog.Commands.Clear();
            RecordCommand(BattleCommandType.SetBoss, bossId: bossId);
            RefreshAllViews();
            OnBossChanged?.Invoke(bossId);
            _network?.NotifyLocalStateChanged();
        }

        public string ExportSnapshotJson()
        {
            _lastSnapshotJson = BattleStateCodec.Serialize(State, Engine.BossId);
            return _lastSnapshotJson;
        }

        public bool ImportSnapshotJson(string json)
        {
            try
            {
                var (snapshot, importedBossId) = BattleStateCodec.Deserialize(json);
                bossId = importedBossId;
                Engine.RestoreState(snapshot, importedBossId);
                RefreshAllViews();
                LogLatest();
                if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                    OnBattleEnded?.Invoke();
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] Snapshot import failed: {ex.Message}");
                return false;
            }
        }

        public bool RestoreLastSnapshot() =>
            !string.IsNullOrEmpty(_lastSnapshotJson) && ImportSnapshotJson(_lastSnapshotJson);

        public void SaveCheckpoint() => ExportSnapshotJson();

        public string ExportCommandLogJson() => CommandLog.ToJson();

        public bool ReplayFromCommandLogJson(string json)
        {
            try
            {
                return ReplayFromCommandLog(BattleCommandLog.FromJson(json));
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] Replay import failed: {ex.Message}");
                return false;
            }
        }

        public bool ReplayFromCommandLog(BattleCommandLog log)
        {
            if (log == null || log.Commands.Count == 0)
            {
                Debug.LogWarning("[Aetherboard] Replay log is empty.");
                return false;
            }

            randomSeed = log.RandomSeed;
            bossId = log.BossId;
            CommandLog.RandomSeed = log.RandomSeed;
            CommandLog.BossId = log.BossId;
            CommandLog.Commands.Clear();
            foreach (var cmd in log.Commands)
                CommandLog.Record(cmd);

            var replayed = BattleReplayer.Replay(log);
            Engine.RestoreState(replayed, log.BossId);
            RefreshAllViews();
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
            Debug.Log($"[Aetherboard] Replayed {log.Commands.Count} commands (seed={log.RandomSeed}, boss={log.BossId}).");
            return true;
        }

        public string DefaultReplayFilePath =>
            Path.Combine(Application.persistentDataPath, "aetherboard_last_replay.json");

        public bool SaveCommandLogToFile(string path = null)
        {
            path ??= DefaultReplayFilePath;
            try
            {
                File.WriteAllText(path, ExportCommandLogJson());
                Debug.Log($"[Aetherboard] Command log saved: {path}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] Save replay failed: {ex.Message}");
                return false;
            }
        }

        public bool LoadAndReplayFromFile(string path = null)
        {
            path ??= DefaultReplayFilePath;
            try
            {
                if (!File.Exists(path))
                {
                    Debug.LogWarning($"[Aetherboard] Replay file not found: {path}");
                    return false;
                }
                return ReplayFromCommandLogJson(File.ReadAllText(path));
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Aetherboard] Load replay failed: {ex.Message}");
                return false;
            }
        }

        public void RefreshAllViews()
        {
            tableView?.Bind(State);
            telegraphVfx?.ShowPreview(State.PreviewCells, State.Boss.Telegraph);
            bossView?.Bind(State.Boss, Engine.BossId);
            OnPhaseChanged?.Invoke(State.Phase);
        }

        public bool TryMove(string unitId, GridPos dest)
        {
            if (_network != null && !_network.IsAuthoritative)
                return _network.SubmitMove(unitId, dest);

            if (!Engine.MoveUnit(unitId, dest)) return false;
            RecordCommand(BattleCommandType.Move, unitId, target: dest);
            tableView?.Bind(State);
            LogLatest();
            _network?.NotifyLocalStateChanged();
            return true;
        }

        public bool TryUseSkill(string unitId, string skillId, GridPos? target = null)
        {
            if (_network != null && !_network.IsAuthoritative)
                return _network.SubmitSkill(unitId, skillId, target);

            if (!Engine.UseSkill(unitId, skillId, target)) return false;
            if (skillId == "interrupt" && State.Boss.FuryCastTurns < 0)
                OnCastInterrupted?.Invoke();
            RecordCommand(BattleCommandType.Skill, unitId, skillId, target);
            tableView?.Bind(State);
            bossView?.Bind(State.Boss, Engine.BossId);
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
            _network?.NotifyLocalStateChanged();
            return true;
        }

        public void EndCurrentPhase()
        {
            if (_network != null && !_network.IsAuthoritative)
            {
                _network.SubmitEndPhase();
                return;
            }

            RecordCommand(BattleCommandType.EndPhase);
            Engine.EndPhase();
            RefreshAllViews();
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
            _network?.NotifyLocalStateChanged();
        }

        public void StepAuto()
        {
            Engine.StepAuto();
            RefreshAllViews();
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
            _network?.NotifyLocalStateChanged();
        }

        private void LogLatest()
        {
            if (State.Log.Count > 0)
                OnLogAdded?.Invoke(State.Log[^1]);
        }

        private void RecordCommand(
            BattleCommandType type,
            string unitId = null,
            string skillId = null,
            GridPos? target = null,
            string bossId = null)
        {
            CommandLog.Record(new BattleCommand
            {
                Turn = State.Turn,
                Phase = State.Phase,
                Type = type,
                UnitId = unitId,
                SkillId = skillId,
                TargetX = target?.X ?? -1,
                TargetY = target?.Y ?? -1,
                BossId = bossId
            });
        }
    }
}
