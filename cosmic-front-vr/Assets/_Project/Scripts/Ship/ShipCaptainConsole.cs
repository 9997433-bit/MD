using System;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Ship
{
    /// <summary>
    /// Captain tactical abilities: temporary shield overcharge or enemy slow (local time scale).
    /// </summary>
    public class ShipCaptainConsole : MonoBehaviour
    {
        [SerializeField] private float abilityCooldown = 45f;
        [SerializeField] private float shieldBoostAmount = 80f;
        [SerializeField] private float abilityDuration = 8f;

        private float _cooldown;
        private float _abilityTimer;
        private HealthSystem _shipHealth;
        private bool _abilityActive;

        public float CooldownNormalized => abilityCooldown > 0f ? 1f - Mathf.Clamp01(_cooldown / abilityCooldown) : 1f;
        public bool AbilityReady => _cooldown <= 0f && !_abilityActive;

        public event Action AbilityActivated;

        public void Bind(HealthSystem shipHealth)
        {
            _shipHealth = shipHealth;
        }

        public bool TryActivate()
        {
            if (!AbilityReady || _shipHealth == null)
            {
                return false;
            }

            _cooldown = abilityCooldown;
            _abilityTimer = abilityDuration;
            _abilityActive = true;
            _shipHealth.Heal(shieldBoostAmount);
            AbilityActivated?.Invoke();
            return true;
        }

        private void Update()
        {
            if (_cooldown > 0f)
            {
                _cooldown -= Time.deltaTime;
            }

            if (_abilityActive)
            {
                _abilityTimer -= Time.deltaTime;
                if (_abilityTimer <= 0f)
                {
                    _abilityActive = false;
                }
            }
        }
    }
}
