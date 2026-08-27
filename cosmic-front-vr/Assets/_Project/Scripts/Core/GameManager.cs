using System;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Core
{
    /// <summary>
    /// Singleton game flow: Hangar -> Battle -> Results.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [SerializeField] private string hangarScene = "Hangar";
        [SerializeField] private string battleScene = "Map_ColonyRim";
        [SerializeField] private float matchDurationSeconds = 600f;

        public GamePhase Phase { get; private set; } = GamePhase.Boot;
        public TeamId SelectedTeam { get; private set; } = TeamId.Terran;
        public MechArchetype SelectedMech { get; private set; } = MechArchetype.Light;
        public float MatchTimeRemaining { get; private set; }
        public int PlayerKills { get; private set; }
        public int PlayerDeaths { get; private set; }

        public event Action<GamePhase> PhaseChanged;
        public event Action MatchEnded;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        public void SelectLoadout(TeamId team, MechArchetype mech)
        {
            SelectedTeam = team;
            SelectedMech = mech;
        }

        public void StartSinglePlayerMission()
        {
            MatchTimeRemaining = matchDurationSeconds;
            PlayerKills = 0;
            PlayerDeaths = 0;
            SetPhase(GamePhase.Loading);
            UnityEngine.SceneManagement.SceneManager.LoadScene(battleScene);
        }

        public void OnBattleSceneLoaded()
        {
            SetPhase(GamePhase.Battle);
        }

        public void RegisterKill()
        {
            PlayerKills++;
        }

        public void RegisterDeath()
        {
            PlayerDeaths++;
        }

        public void EndMatch()
        {
            SetPhase(GamePhase.Results);
            MatchEnded?.Invoke();
        }

        public void ReturnToHangar()
        {
            SetPhase(GamePhase.Hangar);
            UnityEngine.SceneManagement.SceneManager.LoadScene(hangarScene);
        }

        private void Update()
        {
            if (Phase != GamePhase.Battle)
            {
                return;
            }

            MatchTimeRemaining -= Time.deltaTime;
            if (MatchTimeRemaining <= 0f)
            {
                EndMatch();
            }
        }

        private void SetPhase(GamePhase phase)
        {
            Phase = phase;
            PhaseChanged?.Invoke(phase);
        }
    }
}
