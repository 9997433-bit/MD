using System;
using System.Collections;
using FishNet.Object;
using FishNet.Object.Synchronizing;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Network
{
    /// <summary>
    /// Server-authoritative HP sync for networked mechs.
    /// </summary>
    [RequireComponent(typeof(HealthSystem))]
    public class NetworkHealthSync : NetworkBehaviour
    {
        [SerializeField] private float respawnDelaySeconds = 10f;

        private HealthSystem _health;
        private Vector3 _spawnPosition;
        private Quaternion _spawnRotation;
        private bool _deathHandled;

        private readonly SyncVar<float> _syncHealth = new();
        private readonly SyncVar<float> _syncShield = new();
        private readonly SyncVar<bool> _syncAlive = new(true);

        public bool IsAlive => _syncAlive.Value;

        private void Awake()
        {
            _health = GetComponent<HealthSystem>();
            _spawnPosition = transform.position;
            _spawnRotation = transform.rotation;

            _syncHealth.OnChange += OnHealthSyncChanged;
            _syncShield.OnChange += OnShieldSyncChanged;
            _syncAlive.OnChange += OnAliveSyncChanged;
        }

        public override void OnStartServer()
        {
            PushHealthToSyncVars();
            _health.Died += OnServerDied;
        }

        public override void OnStopServer()
        {
            _health.Died -= OnServerDied;
        }

        public override void OnStartClient()
        {
            ApplySyncToLocalHealth();
        }

        private void Update()
        {
            if (IsServerInitialized)
            {
                PushHealthToSyncVars();
            }
        }

        private void OnServerDied(HealthSystem _, GameObject killer)
        {
            if (_deathHandled)
            {
                return;
            }

            _deathHandled = true;
            _syncAlive.Value = false;
            gameObject.SetActive(false);

            if (NetworkScoreManager.Instance != null)
            {
                NetworkScoreManager.Instance.RegisterFrag(killer, gameObject);
            }

            StartCoroutine(ServerRespawnRoutine());
        }

        private IEnumerator ServerRespawnRoutine()
        {
            yield return new WaitForSeconds(respawnDelaySeconds);

            _health.Configure(_health.Team, _health.MaxHealth, _health.MaxShield);
            transform.SetPositionAndRotation(_spawnPosition, _spawnRotation);
            _deathHandled = false;
            _syncAlive.Value = true;
            PushHealthToSyncVars();
            gameObject.SetActive(true);
        }

        public void SetSpawnPoint(Vector3 position, Quaternion rotation)
        {
            _spawnPosition = position;
            _spawnRotation = rotation;
        }

        private void PushHealthToSyncVars()
        {
            if (_health == null)
            {
                return;
            }

            _syncHealth.Value = _health.CurrentHealth;
            _syncShield.Value = _health.CurrentShield;
        }

        private void OnHealthSyncChanged(float prev, float next, bool asServer)
        {
            ApplySyncToLocalHealth();
        }

        private void OnShieldSyncChanged(float prev, float next, bool asServer)
        {
            ApplySyncToLocalHealth();
        }

        private void OnAliveSyncChanged(bool prev, bool next, bool asServer)
        {
            if (IsServerInitialized)
            {
                return;
            }

            gameObject.SetActive(next);
        }

        private void ApplySyncToLocalHealth()
        {
            if (_health == null || IsServerInitialized)
            {
                return;
            }

            _health.SetFromNetwork(_syncHealth.Value, _syncShield.Value);
        }
    }
}
