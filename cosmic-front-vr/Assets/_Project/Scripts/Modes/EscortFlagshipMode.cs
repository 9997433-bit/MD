using System;
using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Ship;
using FishNet;
using FishNet.Object;
using FishNet.Object.Synchronizing;

namespace CosmicFront.Modes
{
    /// <summary>
    /// Escort mode: defenders protect a flagship moving along waypoints; attackers destroy it.
    /// Terran = defender by default, Orbital = attacker (or flipped via inspector).
    /// </summary>
    public class EscortFlagshipMode : NetworkBehaviour
    {
        [SerializeField] private GameObject flagshipPrefab;
        [SerializeField] private Transform[] waypoints;
        [SerializeField] private TeamId defenderTeam = TeamId.Terran;
        [SerializeField] private float cruiseSpeed = 4f;
        [SerializeField] private float waypointReachDistance = 5f;
        [SerializeField] private float matchTimeLimit = 480f;

        private readonly SyncVar<float> _progress = new();
        private readonly SyncVar<bool> _flagshipAlive = new(true);
        private readonly SyncVar<bool> _escortSucceeded = new();
        private readonly SyncVar<int> _waypointIndex = new();

        private ShipController _flagship;
        private HealthSystem _flagshipHealth;
        private bool _running;
        private bool _ended;

        public float Progress => _progress.Value;
        public bool FlagshipAlive => _flagshipAlive.Value;
        public bool EscortSucceeded => _escortSucceeded.Value;
        public TeamId DefenderTeam => defenderTeam;
        public TeamId AttackerTeam => defenderTeam == TeamId.Terran ? TeamId.Orbital : TeamId.Terran;

        public event Action StatusChanged;
        public event Action<bool> EscortEnded;

        public override void OnStartServer()
        {
            if (GameManager.Instance != null &&
                GameManager.Instance.SelectedGameMode != GameModeType.EscortFlagship)
            {
                enabled = false;
                return;
            }

            SpawnFlagship();
            _running = true;
        }

        private void Start()
        {
            // Single-player path (no FishNet server).
            if (InstanceFinder.NetworkManager != null && InstanceFinder.NetworkManager.IsClientOnlyStarted)
            {
                return;
            }

            if (IsServerInitialized)
            {
                return;
            }

            if (GameManager.Instance != null &&
                GameManager.Instance.SelectedGameMode != GameModeType.EscortFlagship)
            {
                enabled = false;
                return;
            }

            if (GameManager.Instance != null && GameManager.Instance.IsMultiplayer)
            {
                return;
            }

            SpawnFlagship();
            _running = true;
            _flagshipAlive.Value = true;
        }

        private void Update()
        {
            if (!_running || _ended)
            {
                return;
            }

            var isAuthority = IsServerInitialized ||
                              (GameManager.Instance != null && !GameManager.Instance.IsMultiplayer);
            if (!isAuthority)
            {
                return;
            }

            if (_flagship == null || _flagshipHealth == null || !_flagshipHealth.IsAlive)
            {
                FailEscort();
                return;
            }

            TickCruise();
        }

        private void SpawnFlagship()
        {
            if (flagshipPrefab == null || waypoints == null || waypoints.Length == 0)
            {
                Debug.LogWarning("[EscortFlagshipMode] Missing prefab or waypoints.");
                return;
            }

            var start = waypoints[0];
            var go = Instantiate(flagshipPrefab, start.position, start.rotation);
            _flagship = go.GetComponent<ShipController>();
            _flagship?.ApplyTeam(defenderTeam);
            _flagshipHealth = go.GetComponent<HealthSystem>();

            if (_flagshipHealth != null)
            {
                // Flagship is tougher.
                _flagshipHealth.Configure(defenderTeam, 1200f, 400f);
                _flagshipHealth.Died += OnFlagshipDied;
            }

            var nm = InstanceFinder.NetworkManager;
            var nob = go.GetComponent<NetworkObject>();
            if (nm != null && nm.IsServerStarted && nob != null)
            {
                nm.ServerManager.Spawn(nob);
            }

            _waypointIndex.Value = 1;
            _progress.Value = 0f;
            StatusChanged?.Invoke();
        }

        private void TickCruise()
        {
            if (waypoints == null || waypoints.Length < 2 || _flagship == null)
            {
                return;
            }

            var index = Mathf.Clamp(_waypointIndex.Value, 0, waypoints.Length - 1);
            var target = waypoints[index];
            var pos = _flagship.transform.position;
            var next = Vector3.MoveTowards(pos, target.position, cruiseSpeed * Time.deltaTime);
            _flagship.transform.position = next;
            var dir = target.position - pos;
            if (dir.sqrMagnitude > 0.01f)
            {
                _flagship.transform.rotation = Quaternion.Slerp(
                    _flagship.transform.rotation,
                    Quaternion.LookRotation(dir.normalized),
                    Time.deltaTime * 2f);
            }

            if (Vector3.Distance(next, target.position) <= waypointReachDistance)
            {
                if (index >= waypoints.Length - 1)
                {
                    SucceedEscort();
                    return;
                }

                _waypointIndex.Value = index + 1;
            }

            _progress.Value = (float)_waypointIndex.Value / (waypoints.Length - 1);
            StatusChanged?.Invoke();
        }

        private void OnFlagshipDied(HealthSystem _, GameObject killer)
        {
            FailEscort();
        }

        private void SucceedEscort()
        {
            if (_ended)
            {
                return;
            }

            _ended = true;
            _running = false;
            _escortSucceeded.Value = true;
            _progress.Value = 1f;
            NotifyEnd(true);
        }

        private void FailEscort()
        {
            if (_ended)
            {
                return;
            }

            _ended = true;
            _running = false;
            _flagshipAlive.Value = false;
            _escortSucceeded.Value = false;
            NotifyEnd(false);
        }

        private void NotifyEnd(bool success)
        {
            StatusChanged?.Invoke();
            EscortEnded?.Invoke(success);

            if (IsServerInitialized)
            {
                EndObserversRpc(success);
            }
            else
            {
                ApplyLocalEnd(success);
            }
        }

        [ObserversRpc]
        private void EndObserversRpc(bool success)
        {
            ApplyLocalEnd(success);
        }

        private void ApplyLocalEnd(bool success)
        {
            if (GameManager.Instance == null)
            {
                return;
            }

            GameManager.Instance.SetModeResult(
                success
                    ? $"护送成功 — {defenderTeam} 旗舰抵达"
                    : $"护送失败 — 旗舰被击沉（{AttackerTeam} 胜利）");
            GameManager.Instance.EndMatchFromNetwork();
        }

        public string BuildStatusText()
        {
            if (!_flagshipAlive.Value)
            {
                return "旗舰已击沉 — 进攻方胜利";
            }

            if (_escortSucceeded.Value)
            {
                return "旗舰抵达终点 — 护送方胜利";
            }

            return $"护送进度 {Mathf.RoundToInt(Progress * 100f)}%  |  航点 {_waypointIndex.Value}/{Mathf.Max(1, waypoints.Length - 1)}";
        }
    }
}
