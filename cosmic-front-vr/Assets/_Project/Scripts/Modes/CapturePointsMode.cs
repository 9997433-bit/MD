using System;
using System.Text;
using UnityEngine;
using CosmicFront.Core;
using FishNet;
using FishNet.Object;
using FishNet.Object.Synchronizing;

namespace CosmicFront.Modes
{
    /// <summary>
    /// Contested capture zone. Ownership changes based on which team has more mechs/ships inside.
    /// </summary>
    public class CapturePoint : NetworkBehaviour
    {
        [SerializeField] private string pointName = "Alpha";
        [SerializeField] private float radius = 12f;
        [SerializeField] private float captureRate = 0.25f;
        [SerializeField] private TeamId startingOwner = TeamId.None;

        private readonly SyncVar<TeamId> _owner = new();
        private readonly SyncVar<float> _captureProgress = new(); // -1 Orbital ... 0 Neutral ... +1 Terran
        private readonly SyncVar<TeamId> _contesting = new();

        public string PointName => pointName;
        public TeamId Owner => _owner.Value;
        public float CaptureProgress => _captureProgress.Value;
        public float Radius => radius;

        public event Action Changed;

        public override void OnStartServer()
        {
            _owner.Value = startingOwner;
            _captureProgress.Value = startingOwner == TeamId.Terran ? 1f :
                startingOwner == TeamId.Orbital ? -1f : 0f;
        }

        private void Start()
        {
            if (IsServerInitialized)
            {
                return;
            }

            if (GameManager.Instance != null && GameManager.Instance.IsMultiplayer)
            {
                return;
            }

            _owner.Value = startingOwner;
            _captureProgress.Value = startingOwner == TeamId.Terran ? 1f :
                startingOwner == TeamId.Orbital ? -1f : 0f;
        }

        private void Update()
        {
            var authority = IsServerInitialized ||
                            (GameManager.Instance != null && !GameManager.Instance.IsMultiplayer);
            if (!authority)
            {
                return;
            }

            TickCapture();
        }

        private void TickCapture()
        {
            CountPresence(out var terran, out var orbital);
            TeamId pressure = TeamId.None;
            if (terran > orbital)
            {
                pressure = TeamId.Terran;
            }
            else if (orbital > terran)
            {
                pressure = TeamId.Orbital;
            }

            _contesting.Value = pressure;

            if (pressure == TeamId.None)
            {
                Changed?.Invoke();
                return;
            }

            var delta = captureRate * Time.deltaTime * (pressure == TeamId.Terran ? 1f : -1f);
            _captureProgress.Value = Mathf.Clamp(_captureProgress.Value + delta, -1f, 1f);

            if (_captureProgress.Value >= 1f)
            {
                _owner.Value = TeamId.Terran;
            }
            else if (_captureProgress.Value <= -1f)
            {
                _owner.Value = TeamId.Orbital;
            }
            else if (Mathf.Abs(_captureProgress.Value) < 0.05f)
            {
                _owner.Value = TeamId.None;
            }

            Changed?.Invoke();
        }

        private void CountPresence(out int terran, out int orbital)
        {
            terran = 0;
            orbital = 0;
            var healths = FindObjectsOfType<HealthSystem>();
            foreach (var h in healths)
            {
                if (!h.IsAlive)
                {
                    continue;
                }

                if (Vector3.Distance(h.transform.position, transform.position) > radius)
                {
                    continue;
                }

                if (h.Team == TeamId.Terran)
                {
                    terran++;
                }
                else if (h.Team == TeamId.Orbital)
                {
                    orbital++;
                }
            }
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(0.2f, 0.8f, 1f, 0.35f);
            Gizmos.DrawWireSphere(transform.position, radius);
        }
    }

    /// <summary>
    /// Capture-points match controller: first team to hold majority for scoreLimit wins, or highest at time-up.
    /// </summary>
    public class CapturePointsMode : NetworkBehaviour
    {
        [SerializeField] private CapturePoint[] points;
        [SerializeField] private float scoreTickInterval = 2f;
        [SerializeField] private int scoreLimit = 100;

        private readonly SyncVar<int> _terranHoldScore = new();
        private readonly SyncVar<int> _orbitalHoldScore = new();
        private float _tick;

        public int TerranHoldScore => _terranHoldScore.Value;
        public int OrbitalHoldScore => _orbitalHoldScore.Value;

        public event Action StatusChanged;

        private void Start()
        {
            if (GameManager.Instance != null &&
                GameManager.Instance.SelectedGameMode != GameModeType.CapturePoints)
            {
                enabled = false;
                return;
            }

            if (points == null || points.Length == 0)
            {
                points = FindObjectsOfType<CapturePoint>();
            }

            foreach (var p in points)
            {
                if (p != null)
                {
                    p.Changed += () => StatusChanged?.Invoke();
                }
            }
        }

        private void Update()
        {
            if (GameManager.Instance != null &&
                GameManager.Instance.SelectedGameMode != GameModeType.CapturePoints)
            {
                return;
            }

            var authority = IsServerInitialized ||
                            (GameManager.Instance != null && !GameManager.Instance.IsMultiplayer);
            if (!authority)
            {
                return;
            }

            _tick += Time.deltaTime;
            if (_tick < scoreTickInterval)
            {
                return;
            }

            _tick = 0f;
            TickHoldScore();
        }

        private void TickHoldScore()
        {
            if (points == null)
            {
                return;
            }

            foreach (var p in points)
            {
                if (p == null)
                {
                    continue;
                }

                if (p.Owner == TeamId.Terran)
                {
                    _terranHoldScore.Value++;
                }
                else if (p.Owner == TeamId.Orbital)
                {
                    _orbitalHoldScore.Value++;
                }
            }

            StatusChanged?.Invoke();

            if (_terranHoldScore.Value >= scoreLimit || _orbitalHoldScore.Value >= scoreLimit)
            {
                var terranWins = _terranHoldScore.Value >= scoreLimit;
                EndMatch(terranWins);
            }
        }

        private void EndMatch(bool terranWins)
        {
            var msg = terranWins
                ? $"据点胜利 — 地球联合 {_terranHoldScore.Value}:{_orbitalHoldScore.Value}"
                : $"据点胜利 — 轨道联盟 {_orbitalHoldScore.Value}:{_terranHoldScore.Value}";

            if (IsServerInitialized)
            {
                EndObserversRpc(msg);
            }
            else
            {
                ApplyEnd(msg);
            }
        }

        [ObserversRpc]
        private void EndObserversRpc(string msg)
        {
            ApplyEnd(msg);
        }

        private void ApplyEnd(string msg)
        {
            GameManager.Instance?.SetModeResult(msg);
            GameManager.Instance?.EndMatchFromNetwork();
        }

        public string BuildStatusText()
        {
            var sb = new StringBuilder();
            sb.AppendLine($"据点分 TU {_terranHoldScore.Value}  |  OL {_orbitalHoldScore.Value} / {scoreLimit}");
            if (points == null)
            {
                return sb.ToString();
            }

            foreach (var p in points)
            {
                if (p == null)
                {
                    continue;
                }

                sb.AppendLine($"{p.PointName}: {p.Owner} ({p.CaptureProgress:F1})");
            }

            return sb.ToString();
        }
    }
}
