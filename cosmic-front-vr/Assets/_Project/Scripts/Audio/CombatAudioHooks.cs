using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.Audio
{
    /// <summary>
    /// Mech combat audio hooks: fire / hit / death. Attach to mech root with HealthSystem.
    /// </summary>
    public class CombatAudioHooks : MonoBehaviour
    {
        [SerializeField] private AudioSource reservedSource;
        [SerializeField] private float primaryFireAudioInterval = 0.125f;

        private HealthSystem _health;
        private IMechInputProvider _input;
        private float _fireAudioCooldown;
        private float _prevHealth;
        private float _prevShield;
        private bool _statsReady;

        private void Awake()
        {
            _health = GetComponent<HealthSystem>();
            _input = GetComponent<MechInputRouter>() ?? GetComponent<IMechInputProvider>();
            GameAudioBus.EnsureExists();
        }

        private void OnEnable()
        {
            if (_health == null)
            {
                return;
            }

            _health.Died += OnDied;
            _health.HealthChanged += OnHealthChanged;
            _prevHealth = _health.CurrentHealth;
            _prevShield = _health.CurrentShield;
            _statsReady = true;
        }

        private void OnDisable()
        {
            if (_health == null)
            {
                return;
            }

            _health.Died -= OnDied;
            _health.HealthChanged -= OnHealthChanged;
        }

        private void Update()
        {
            if (_fireAudioCooldown > 0f)
            {
                _fireAudioCooldown -= Time.deltaTime;
            }

            if (_health != null && !_health.IsAlive)
            {
                return;
            }

            if (_input == null || _fireAudioCooldown > 0f)
            {
                return;
            }

            if (_input.ReadInput().FirePrimary)
            {
                GameAudioBus.Instance?.PlayOneShot("mech_fire");
                _fireAudioCooldown = primaryFireAudioInterval;
            }
        }

        private void OnHealthChanged(float health, float maxHealth, float shield, float maxShield)
        {
            if (_statsReady && health > 0f && (health < _prevHealth || shield < _prevShield))
            {
                GameAudioBus.Instance?.PlayOneShot("mech_hit");
            }

            _prevHealth = health;
            _prevShield = shield;
            _statsReady = true;
        }

        private void OnDied(HealthSystem _, GameObject killer)
        {
            GameAudioBus.Instance?.PlayOneShot("mech_death");
        }
    }
}
