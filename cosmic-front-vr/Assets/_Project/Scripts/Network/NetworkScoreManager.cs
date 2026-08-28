using System;
using System.Text;
using FishNet.Object;
using FishNet.Object.Synchronizing;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Network
{
    [Serializable]
    public struct PlayerScoreEntry
    {
        public int ClientId;
        public int Kills;
        public int Deaths;
        public TeamId Team;
    }

    /// <summary>
    /// Server-authoritative match timer and frag tracking.
    /// </summary>
    public class NetworkScoreManager : NetworkBehaviour
    {
        public static NetworkScoreManager Instance { get; private set; }

        [SerializeField] private float matchDurationSeconds = 600f;

        private readonly SyncVar<float> _timeRemaining = new();
        private readonly SyncVar<int> _terranScore = new();
        private readonly SyncVar<int> _orbitalScore = new();
        private readonly SyncList<PlayerScoreEntry> _playerScores = new();

        public float TimeRemaining => _timeRemaining.Value;
        public int TerranScore => _terranScore.Value;
        public int OrbitalScore => _orbitalScore.Value;
        public SyncList<PlayerScoreEntry> PlayerScores => _playerScores;

        public event Action ScoresChanged;
        public event Action MatchEnded;

        private bool _matchEnded;

        private void Awake()
        {
            Instance = this;
            _playerScores.OnChange += OnPlayerScoresChanged;
            _timeRemaining.OnChange += OnTimerChanged;
            _terranScore.OnChange += OnTeamScoreChanged;
            _orbitalScore.OnChange += OnTeamScoreChanged;
        }

        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }

        public override void OnStartServer()
        {
            _timeRemaining.Value = matchDurationSeconds;
            _terranScore.Value = 0;
            _orbitalScore.Value = 0;
            _playerScores.Clear();
        }

        private void Update()
        {
            if (!IsServerInitialized || _matchEnded)
            {
                return;
            }

            _timeRemaining.Value = Mathf.Max(0f, _timeRemaining.Value - Time.deltaTime);

            if (GameManager.Instance != null)
            {
                GameManager.Instance.SetNetworkMatchTime(_timeRemaining.Value);
            }

            if (_timeRemaining.Value <= 0f)
            {
                EndMatchServer();
            }
        }

        public void RegisterFrag(GameObject killer, GameObject victim)
        {
            if (!IsServerInitialized || killer == null || victim == null)
            {
                return;
            }

            var killerHealth = killer.GetComponentInParent<HealthSystem>();
            var victimHealth = victim.GetComponentInParent<HealthSystem>();
            if (killerHealth == null || victimHealth == null)
            {
                return;
            }

            if (killerHealth.Team != TeamId.None && killerHealth.Team == victimHealth.Team)
            {
                return;
            }

            IncrementTeamScore(killerHealth.Team);

            var killerConn = killer.GetComponentInParent<NetworkMechSync>()?.Owner;
            var victimConn = victim.GetComponentInParent<NetworkMechSync>()?.Owner;

            if (killerConn != null)
            {
                AddPlayerKill(killerConn.ClientId, killerHealth.Team);
            }

            if (victimConn != null)
            {
                AddPlayerDeath(victimConn.ClientId, victimHealth.Team);
            }

            NotifyOwnerStats(killerConn, victimConn);
        }

        private void IncrementTeamScore(TeamId team)
        {
            switch (team)
            {
                case TeamId.Terran:
                    _terranScore.Value++;
                    break;
                case TeamId.Orbital:
                    _orbitalScore.Value++;
                    break;
            }
        }

        private void AddPlayerKill(int clientId, TeamId team)
        {
            for (var i = 0; i < _playerScores.Count; i++)
            {
                if (_playerScores[i].ClientId != clientId)
                {
                    continue;
                }

                var entry = _playerScores[i];
                entry.Kills++;
                _playerScores[i] = entry;
                return;
            }

            _playerScores.Add(new PlayerScoreEntry
            {
                ClientId = clientId,
                Kills = 1,
                Deaths = 0,
                Team = team
            });
        }

        private void AddPlayerDeath(int clientId, TeamId team)
        {
            for (var i = 0; i < _playerScores.Count; i++)
            {
                if (_playerScores[i].ClientId != clientId)
                {
                    continue;
                }

                var entry = _playerScores[i];
                entry.Deaths++;
                _playerScores[i] = entry;
                return;
            }

            _playerScores.Add(new PlayerScoreEntry
            {
                ClientId = clientId,
                Kills = 0,
                Deaths = 1,
                Team = team
            });
        }

        private void NotifyOwnerStats(FishNet.Connection.NetworkConnection killerConn,
            FishNet.Connection.NetworkConnection victimConn)
        {
            if (killerConn != null && killerConn.IsActive)
            {
                var entry = FindEntry(killerConn.ClientId);
                TargetUpdatePersonalStats(killerConn, entry.Kills, entry.Deaths);
            }

            if (victimConn != null && victimConn.IsActive)
            {
                var entry = FindEntry(victimConn.ClientId);
                TargetUpdatePersonalStats(victimConn, entry.Kills, entry.Deaths);
            }
        }

        private PlayerScoreEntry FindEntry(int clientId)
        {
            for (var i = 0; i < _playerScores.Count; i++)
            {
                if (_playerScores[i].ClientId == clientId)
                {
                    return _playerScores[i];
                }
            }

            return default;
        }

        [TargetRpc]
        private void TargetUpdatePersonalStats(FishNet.Connection.NetworkConnection conn, int kills, int deaths)
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SetPersonalStats(kills, deaths);
            }
        }

        private void EndMatchServer()
        {
            if (_matchEnded)
            {
                return;
            }

            _matchEnded = true;
            EndMatchObserversRpc();
        }

        [ObserversRpc]
        private void EndMatchObserversRpc()
        {
            MatchEnded?.Invoke();
            GameManager.Instance?.EndMatchFromNetwork();
        }

        public string BuildScoreboardText()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"TU {TerranScore}  |  OL {OrbitalScore}");
            sb.AppendLine($"Time {Mathf.CeilToInt(TimeRemaining)}s");

            for (var i = 0; i < _playerScores.Count; i++)
            {
                var e = _playerScores[i];
                sb.AppendLine($"P{e.ClientId} [{e.Team}] K{e.Kills} D{e.Deaths}");
            }

            return sb.ToString();
        }

        private void OnPlayerScoresChanged(SyncListOperation op, int index, PlayerScoreEntry oldItem,
            PlayerScoreEntry newItem, bool asServer)
        {
            ScoresChanged?.Invoke();
        }

        private void OnTimerChanged(float prev, float next, bool asServer)
        {
            ScoresChanged?.Invoke();
        }

        private void OnTeamScoreChanged(int prev, int next, bool asServer)
        {
            ScoresChanged?.Invoke();
        }
    }
}
