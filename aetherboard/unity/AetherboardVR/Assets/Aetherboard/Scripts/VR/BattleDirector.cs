using System;
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

        public BattleCommandLog CommandLog { get; } = new();
        private string _lastSnapshotJson;
        private IBattleNetworkBridge _network;

        public void SetNetworkBridge(IBattleNetworkBridge bridge) => _network = bridge;

        private void Awake()
        {
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
            Engine.Reset(randomSeed, bossId);
            CommandLog.BossId = bossId;
            CommandLog.Commands.Clear();
            RecordCommand(BattleCommandType.SetBoss, bossId: bossId);
            RefreshAllViews();
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

        public void RefreshAllViews()
        {
            tableView?.Bind(State);
            telegraphVfx?.ShowPreview(State.PreviewCells, State.Boss.Telegraph);
            bossView?.Bind(State.Boss);
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
            return true;
        }

        public bool TryUseSkill(string unitId, string skillId, GridPos? target = null)
        {
            if (_network != null && !_network.IsAuthoritative)
                return _network.SubmitSkill(unitId, skillId, target);

            if (!Engine.UseSkill(unitId, skillId, target)) return false;
            RecordCommand(BattleCommandType.Skill, unitId, skillId, target);
            tableView?.Bind(State);
            bossView?.Bind(State.Boss);
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
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
        }

        public void StepAuto()
        {
            Engine.StepAuto();
            RefreshAllViews();
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
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
