using System;
using UnityEngine;
using CosmicFront.Network;

namespace CosmicFront.Core
{
    public enum MatchMode
    {
        SinglePlayer,
        MultiplayerHost,
        MultiplayerClient
    }

    /// <summary>
    /// Singleton game flow: Hangar -> Battle -> Results.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [SerializeField] private string hangarScene = "Hangar";
        [SerializeField] private string battleScene = "Map_ColonyRim";
        [SerializeField] private string asteroidScene = "Map_AsteroidField";
        [SerializeField] private float matchDurationSeconds = 600f;

        public GamePhase Phase { get; private set; } = GamePhase.Boot;
        public MatchMode CurrentMatchMode { get; private set; } = MatchMode.SinglePlayer;
        public bool IsMultiplayer => CurrentMatchMode != MatchMode.SinglePlayer;
        public TeamId SelectedTeam { get; private set; } = TeamId.Terran;
        public MechArchetype SelectedMech { get; private set; } = MechArchetype.Light;
        public SpawnPreference SelectedSpawn { get; private set; } = SpawnPreference.Mech;
        public GameModeType SelectedGameMode { get; private set; } = GameModeType.TeamDeathmatch;
        public string SelectedBattleScene { get; private set; }
        public string MultiplayerAddress { get; private set; } = NetworkSessionConfig.DefaultAddress;
        public float MatchTimeRemaining { get; private set; }
        public int PlayerKills { get; private set; }
        public int PlayerDeaths { get; private set; }
        public string ModeResultMessage { get; private set; } = string.Empty;

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

        public void SelectSpawnPreference(SpawnPreference spawn)
        {
            SelectedSpawn = spawn;
        }

        public void SelectGameMode(GameModeType mode)
        {
            SelectedGameMode = mode;
        }

        public void SetModeResult(string message)
        {
            ModeResultMessage = message ?? string.Empty;
        }

        public void SelectBattleScene(string sceneName)
        {
            SelectedBattleScene = string.IsNullOrWhiteSpace(sceneName) ? battleScene : sceneName;
        }

        public string GetActiveBattleScene()
        {
            return string.IsNullOrWhiteSpace(SelectedBattleScene) ? battleScene : SelectedBattleScene;
        }

        public string GetAsteroidSceneName() => asteroidScene;

        public void StartSinglePlayerMission()
        {
            CurrentMatchMode = MatchMode.SinglePlayer;
            BeginMatchLoad();
        }

        public void StartMultiplayerHost()
        {
            ApplySelectedLoadoutFromUiDefaults();
            CurrentMatchMode = MatchMode.MultiplayerHost;
            NetworkBootstrap.StartHost(BeginMatchLoad);
        }

        public void StartMultiplayerClient(string address)
        {
            ApplySelectedLoadoutFromUiDefaults();
            CurrentMatchMode = MatchMode.MultiplayerClient;
            MultiplayerAddress = string.IsNullOrWhiteSpace(address)
                ? NetworkSessionConfig.DefaultAddress
                : address.Trim();
            NetworkBootstrap.StartClient(MultiplayerAddress, OnMultiplayerClientConnected);
        }

        private void OnMultiplayerClientConnected()
        {
            SetPhase(GamePhase.Loading);
        }

        private void BeginMatchLoad()
        {
            MatchTimeRemaining = matchDurationSeconds;
            PlayerKills = 0;
            PlayerDeaths = 0;
            ModeResultMessage = string.Empty;
            SetPhase(GamePhase.Loading);

            if (IsMultiplayer)
            {
                if (NetworkBootstrap.IsServer)
                {
                    NetworkBootstrap.LoadBattleScene(GetActiveBattleScene());
                }

                return;
            }

            UnityEngine.SceneManagement.SceneManager.LoadScene(GetActiveBattleScene());
        }

        private void ApplySelectedLoadoutFromUiDefaults()
        {
            // HangarMenu sets loadout before calling multiplayer start.
        }

        public void OnBattleSceneLoaded()
        {
            SetPhase(GamePhase.Battle);
        }

        public void OnHangarSceneLoaded()
        {
            SetPhase(GamePhase.Hangar);
        }

        public void RegisterKill()
        {
            PlayerKills++;
        }

        public void RegisterDeath()
        {
            PlayerDeaths++;
        }

        public void SetPersonalStats(int kills, int deaths)
        {
            PlayerKills = kills;
            PlayerDeaths = deaths;
        }

        public void SetNetworkMatchTime(float seconds)
        {
            MatchTimeRemaining = seconds;
        }

        public void EndMatchFromNetwork()
        {
            EndMatch();
        }

        public void EndMatch()
        {
            SetPhase(GamePhase.Results);
            MatchEnded?.Invoke();
        }

        public void ReturnToHangar()
        {
            if (IsMultiplayer)
            {
                NetworkBootstrap.Disconnect();
                CurrentMatchMode = MatchMode.SinglePlayer;
            }

            SetPhase(GamePhase.Hangar);
            UnityEngine.SceneManagement.SceneManager.LoadScene(hangarScene);
        }

        private void Update()
        {
            if (Phase != GamePhase.Battle)
            {
                return;
            }

            if (IsMultiplayer && NetworkScoreManager.Instance != null)
            {
                MatchTimeRemaining = NetworkScoreManager.Instance.TimeRemaining;
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
