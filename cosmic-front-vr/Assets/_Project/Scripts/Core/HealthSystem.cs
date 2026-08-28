using System;
using UnityEngine;

namespace CosmicFront.Core
{
    public class HealthSystem : MonoBehaviour, IDamageable
    {
        [SerializeField] private TeamId team = TeamId.None;
        [SerializeField] private float maxHealth = 100f;
        [SerializeField] private float maxShield = 50f;
        [SerializeField] private float shieldRegenDelay = 3f;
        [SerializeField] private float shieldRegenRate = 10f;

        public TeamId Team => team;
        public bool IsAlive => CurrentHealth > 0f;
        public float CurrentHealth { get; private set; }
        public float CurrentShield { get; private set; }
        public float MaxHealth => maxHealth;
        public float MaxShield => maxShield;

        public event Action<HealthSystem, GameObject> Died;
        public event Action<float, float, float, float> HealthChanged;

        private float _shieldRegenTimer;

        private void Awake()
        {
            CurrentHealth = maxHealth;
            CurrentShield = maxShield;
        }

        public void Configure(TeamId newTeam, float health, float shield)
        {
            team = newTeam;
            maxHealth = health;
            maxShield = shield;
            CurrentHealth = health;
            CurrentShield = shield;
            NotifyChanged();
        }

        public void ApplyDamage(float amount, GameObject source)
        {
            if (!IsAlive || amount <= 0f)
            {
                return;
            }

            ApplyDamageInternal(amount, source, invokeDeathEvent: true);
        }

        /// <summary>
        /// Mirror HP from network authority without re-triggering death callbacks.
        /// </summary>
        public void SetFromNetwork(float health, float shield)
        {
            CurrentHealth = health;
            CurrentShield = shield;
            NotifyChanged();
        }

        internal void ApplyDamageInternal(float amount, GameObject source, bool invokeDeathEvent)
        {
            if (!IsAlive || amount <= 0f)
            {
                return;
            }

            _shieldRegenTimer = shieldRegenDelay;
            var remaining = amount;

            if (CurrentShield > 0f)
            {
                var absorbed = Mathf.Min(CurrentShield, remaining);
                CurrentShield -= absorbed;
                remaining -= absorbed;
            }

            if (remaining > 0f)
            {
                CurrentHealth = Mathf.Max(0f, CurrentHealth - remaining);
            }

            NotifyChanged();

            if (invokeDeathEvent && !IsAlive)
            {
                Died?.Invoke(this, source);
            }
        }

        public void Heal(float amount)
        {
            if (!IsAlive)
            {
                return;
            }

            CurrentHealth = Mathf.Min(maxHealth, CurrentHealth + amount);
            NotifyChanged();
        }

        public void RestoreShield(float amount)
        {
            if (!IsAlive || amount <= 0f)
            {
                return;
            }

            CurrentShield = Mathf.Min(maxShield, CurrentShield + amount);
            NotifyChanged();
        }

        private void Update()
        {
            if (!IsAlive || maxShield <= 0f || CurrentShield >= maxShield)
            {
                return;
            }

            if (_shieldRegenTimer > 0f)
            {
                _shieldRegenTimer -= Time.deltaTime;
                return;
            }

            CurrentShield = Mathf.Min(maxShield, CurrentShield + shieldRegenRate * Time.deltaTime);
            NotifyChanged();
        }

        private void NotifyChanged()
        {
            HealthChanged?.Invoke(CurrentHealth, maxHealth, CurrentShield, maxShield);
        }
    }
}
