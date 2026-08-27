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

        private void Awake()
        {
            Engine = new BattleEngine(bossId, randomSeed);
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
            RefreshAllViews();
        }

        public void RefreshAllViews()
        {
            tableView?.Bind(State);
            telegraphVfx?.ShowPreview(State.PreviewCells, State.Boss.Telegraph);
            bossView?.Bind(State.Boss);
            OnPhaseChanged?.Invoke(State.Phase);
        }

        public bool TryMove(string unitId, GridPos dest)
        {
            if (!Engine.MoveUnit(unitId, dest)) return false;
            tableView?.Bind(State);
            LogLatest();
            return true;
        }

        public bool TryUseSkill(string unitId, string skillId, GridPos? target = null)
        {
            if (!Engine.UseSkill(unitId, skillId, target)) return false;
            tableView?.Bind(State);
            bossView?.Bind(State.Boss);
            LogLatest();
            if (State.Phase == BattlePhase.Victory || State.Phase == BattlePhase.Defeat)
                OnBattleEnded?.Invoke();
            return true;
        }

        public void EndCurrentPhase()
        {
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
    }
}
