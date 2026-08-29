using UnityEngine;
using CosmicFront.AI;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Modes;
using FishNet;
using FishNet.Object;

namespace CosmicFront.Modes
{
    /// <summary>
    /// Escort defenders: spawn wingmen that intercept attackers near the flagship.
    /// </summary>
    public class EscortDefenderWing : MonoBehaviour
    {
        [SerializeField] private GameObject defenderPrefab;
        [SerializeField] private int maxDefenders = 3;
        [SerializeField] private float respawnDelay = 12f;
        [SerializeField] private float orbitRadius = 14f;
        [SerializeField] private float retargetInterval = 1.25f;
        [SerializeField] private float interceptRange = 90f;

        private EscortFlagshipMode _escort;
        private int _alive;
        private float _respawnTimer;
        private float _retargetTimer;
        private readonly System.Collections.Generic.List<SimpleEnemyAI> _wing = new();

        private void Awake()
        {
            _escort = GetComponent<EscortFlagshipMode>() ?? FindObjectOfType<EscortFlagshipMode>();
        }

        private void Start()
        {
            if (GameManager.Instance != null &&
                GameManager.Instance.SelectedGameMode != GameModeType.EscortFlagship)
            {
                enabled = false;
                return;
            }

            var nm = InstanceFinder.NetworkManager;
            if (nm != null && nm.IsClientStarted && !nm.IsServerStarted)
            {
                enabled = false;
                return;
            }

            if (defenderPrefab == null)
            {
                var template = FindObjectOfType<SimpleEnemyAI>();
                if (template != null)
                {
                    defenderPrefab = template.gameObject;
                }
            }

            for (var i = 0; i < maxDefenders; i++)
            {
                SpawnDefender(i);
            }
        }

        private void Update()
        {
            if (_escort == null || !_escort.FlagshipAlive || _escort.EscortSucceeded)
            {
                return;
            }

            _retargetTimer -= Time.deltaTime;
            if (_retargetTimer <= 0f)
            {
                RetargetWing();
                _retargetTimer = retargetInterval;
            }

            if (_alive >= maxDefenders)
            {
                return;
            }

            _respawnTimer -= Time.deltaTime;
            if (_respawnTimer <= 0f)
            {
                SpawnDefender(_alive);
                _respawnTimer = respawnDelay;
            }
        }

        private void SpawnDefender(int slot)
        {
            if (defenderPrefab == null || _escort == null)
            {
                return;
            }

            var flagship = _escort.FlagshipTransform;
            if (flagship == null)
            {
                return;
            }

            var angle = slot * Mathf.PI * 2f / Mathf.Max(1, maxDefenders);
            var offset = new Vector3(Mathf.Cos(angle), 0.2f, Mathf.Sin(angle)) * orbitRadius;
            var pos = flagship.position + offset + Vector3.up * 3f;
            var go = Instantiate(defenderPrefab, pos, Quaternion.LookRotation(flagship.forward));

            var mech = go.GetComponent<MechController>();
            mech?.SetTeam(_escort.DefenderTeam);
            mech?.SetModel(_escort.DefenderTeam == TeamId.Terran ? MechModelId.Bastion : MechModelId.Kestrel);

            var ai = go.GetComponent<SimpleEnemyAI>();
            if (ai != null)
            {
                ai.SetTarget(FindNearestAttacker(flagship) ?? flagship);
                _wing.Add(ai);
            }

            var health = go.GetComponent<HealthSystem>();
            if (health != null)
            {
                health.Died += OnDefenderDied;
                _alive++;
            }

            var nm = InstanceFinder.NetworkManager;
            var nob = go.GetComponent<NetworkObject>();
            if (nm != null && nm.IsServerStarted && nob != null)
            {
                nm.ServerManager.Spawn(nob);
            }
        }

        private void RetargetWing()
        {
            var flagship = _escort != null ? _escort.FlagshipTransform : null;
            if (flagship == null)
            {
                return;
            }

            var attacker = FindNearestAttacker(flagship);
            for (var i = _wing.Count - 1; i >= 0; i--)
            {
                var ai = _wing[i];
                if (ai == null)
                {
                    _wing.RemoveAt(i);
                    continue;
                }

                ai.SetTarget(attacker != null ? attacker : flagship);
            }
        }

        private Transform FindNearestAttacker(Transform flagship)
        {
            MechController nearest = null;
            var best = interceptRange * interceptRange;
            var mechs = FindObjectsOfType<MechController>();
            for (var i = 0; i < mechs.Length; i++)
            {
                var m = mechs[i];
                if (m == null || m.Team == _escort.DefenderTeam)
                {
                    continue;
                }

                // Skip other wingmen / self by requiring enemy team only.
                var d = (m.transform.position - flagship.position).sqrMagnitude;
                if (d < best)
                {
                    best = d;
                    nearest = m;
                }
            }

            return nearest != null ? nearest.transform : null;
        }

        private void OnDefenderDied(HealthSystem health, GameObject killer)
        {
            health.Died -= OnDefenderDied;
            _alive = Mathf.Max(0, _alive - 1);
            _respawnTimer = respawnDelay;

            var ai = health.GetComponent<SimpleEnemyAI>();
            if (ai != null)
            {
                _wing.Remove(ai);
            }

            Destroy(health.gameObject, 2f);
        }
    }
}
