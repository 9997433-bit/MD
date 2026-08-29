using System.Collections.Generic;
using UnityEngine;
using CosmicFront.AI;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Ship;
using FishNet;
using FishNet.Object;

namespace CosmicFront.Modes
{
    /// <summary>
    /// Escort P6: spawns attacker mech waves that focus the flagship.
    /// Mount on the same GameObject as <see cref="EscortFlagshipMode"/> (or a sibling).
    /// Leave attackerPrefab empty to resolve via Resources.Load("EnemyMech")
    /// or an in-scene SimpleEnemyAI template at runtime.
    /// </summary>
    public class EscortAttackWaveSpawner : MonoBehaviour
    {
        [SerializeField] private GameObject attackerPrefab;
        [SerializeField] private float waveIntervalSeconds = 18f;
        [SerializeField] private int maxAlive = 6;
        [SerializeField] private int spawnsPerWave = 2;
        [SerializeField] private float forwardOffset = 28f;
        [SerializeField] private float flankOffset = 16f;
        [SerializeField] private float heightOffset = 5f;

        private EscortFlagshipMode _escort;
        private float _timer;
        private bool _active;
        private readonly List<HealthSystem> _alive = new List<HealthSystem>();

        private void Awake()
        {
            _escort = GetComponent<EscortFlagshipMode>() ?? FindObjectOfType<EscortFlagshipMode>();
        }

        private void Start()
        {
            if (!IsEscortSelected() || ShouldDisableOnClient())
            {
                enabled = false;
                return;
            }

            ResolvePrefab();
            _active = true;
            // First wave arrives sooner so escort pressure is visible early.
            _timer = Mathf.Max(3f, waveIntervalSeconds * 0.4f);
        }

        private void Update()
        {
            if (!_active || _escort == null)
            {
                return;
            }

            if (!_escort.FlagshipAlive || _escort.EscortSucceeded)
            {
                _active = false;
                return;
            }

            PruneDead();

            _timer -= Time.deltaTime;
            if (_timer > 0f)
            {
                return;
            }

            _timer = waveIntervalSeconds;
            SpawnWave();
        }

        private void SpawnWave()
        {
            if (attackerPrefab == null)
            {
                ResolvePrefab();
                if (attackerPrefab == null)
                {
                    return;
                }
            }

            var flagship = ResolveFlagship();
            if (flagship == null)
            {
                return;
            }

            var team = _escort.AttackerTeam;
            var toSpawn = Mathf.Min(spawnsPerWave, maxAlive - _alive.Count);
            for (var i = 0; i < toSpawn; i++)
            {
                SpawnOne(flagship, team, i);
            }
        }

        private void SpawnOne(Transform flagship, TeamId team, int slot)
        {
            var pos = GetSpawnPosition(flagship, slot);
            var look = flagship.position - pos;
            var rot = look.sqrMagnitude > 0.01f
                ? Quaternion.LookRotation(look.normalized)
                : flagship.rotation;

            var go = Instantiate(attackerPrefab, pos, rot);
            var mech = go.GetComponent<MechController>();
            if (mech != null)
            {
                mech.SetTeam(team);
            }

            var ai = go.GetComponent<SimpleEnemyAI>();
            if (ai != null)
            {
                ai.SetTarget(flagship);
            }

            var health = go.GetComponent<HealthSystem>();
            if (health != null)
            {
                health.Died += OnAttackerDied;
                _alive.Add(health);
            }

            var nm = InstanceFinder.NetworkManager;
            var nob = go.GetComponent<NetworkObject>();
            if (nm != null && nm.IsServerStarted && nob != null)
            {
                nm.ServerManager.Spawn(nob);
            }
        }

        private Vector3 GetSpawnPosition(Transform flagship, int slot)
        {
            var forward = flagship.forward;
            var right = flagship.right;
            var basePos = flagship.position + forward * forwardOffset + Vector3.up * heightOffset;

            return (slot % 3) switch
            {
                0 => basePos + right * flankOffset,
                1 => basePos - right * flankOffset,
                _ => basePos + forward * (flankOffset * 0.25f)
            };
        }

        private Transform ResolveFlagship()
        {
            if (_escort != null && _escort.FlagshipTransform != null)
            {
                return _escort.FlagshipTransform;
            }

            if (_escort == null)
            {
                return null;
            }

            // Fallback: escort flagship is configured with MaxHealth 1200.
            foreach (var ship in FindObjectsOfType<ShipController>())
            {
                if (ship.Team == _escort.DefenderTeam &&
                    ship.Health != null &&
                    ship.Health.IsAlive &&
                    ship.Health.MaxHealth >= 1000f)
                {
                    return ship.transform;
                }
            }

            return null;
        }

        private void ResolvePrefab()
        {
            if (attackerPrefab != null)
            {
                return;
            }

            attackerPrefab = Resources.Load<GameObject>("EnemyMech");
            if (attackerPrefab != null)
            {
                return;
            }

            var template = FindObjectOfType<SimpleEnemyAI>();
            if (template != null)
            {
                attackerPrefab = template.gameObject;
            }

            if (attackerPrefab == null)
            {
                Debug.LogWarning("[EscortAttackWaveSpawner] No attackerPrefab — assign EnemyMech or place under Resources/EnemyMech.");
            }
        }

        private void OnAttackerDied(HealthSystem health, GameObject killer)
        {
            health.Died -= OnAttackerDied;
            _alive.Remove(health);
            Destroy(health.gameObject, 2f);
        }

        private void PruneDead()
        {
            for (var i = _alive.Count - 1; i >= 0; i--)
            {
                if (_alive[i] == null || !_alive[i].IsAlive)
                {
                    _alive.RemoveAt(i);
                }
            }
        }

        private static bool IsEscortSelected()
        {
            return GameManager.Instance == null ||
                   GameManager.Instance.SelectedGameMode == GameModeType.EscortFlagship;
        }

        private static bool ShouldDisableOnClient()
        {
            var nm = InstanceFinder.NetworkManager;
            return nm != null && nm.IsClientStarted && !nm.IsServerStarted;
        }
    }
}
