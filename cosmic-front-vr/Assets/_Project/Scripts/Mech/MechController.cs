using UnityEngine;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Root controller for player or AI mechs. Attach to root with Rigidbody.
    /// </summary>
    [RequireComponent(typeof(MechMovement))]
    [RequireComponent(typeof(HealthSystem))]
    public class MechController : MonoBehaviour
    {
        [SerializeField] private Transform yawPivot;
        [SerializeField] private Transform pitchPivot;
        [SerializeField] private Transform fireOrigin;
        [SerializeField] private MechArchetype archetype = MechArchetype.Light;
        [SerializeField] private TeamId team = TeamId.Terran;

        private MechMovement _movement;
        private HealthSystem _health;
        private LockOnSystem _lockOn;
        private WeaponPrimary _primary;
        private WeaponSecondary _secondary;
        private IMechInputProvider _input;

        public TeamId Team => team;
        public MechArchetype Archetype => archetype;
        public LockOnSystem LockOn => _lockOn;
        public Transform FireOrigin => fireOrigin != null ? fireOrigin : pitchPivot;

        private void Awake()
        {
            _movement = GetComponent<MechMovement>();
            _health = GetComponent<HealthSystem>();
            _lockOn = GetComponent<LockOnSystem>();
            _primary = GetComponent<WeaponPrimary>();
            _secondary = GetComponent<WeaponSecondary>();
            _input = GetComponent<MechInputRouter>() ?? GetComponent<IMechInputProvider>();

            ApplyArchetype();
            _health.Died += OnDied;
        }

        private void OnDestroy()
        {
            if (_health != null)
            {
                _health.Died -= OnDied;
            }
        }

        public void SetTeam(TeamId newTeam)
        {
            team = newTeam;
            _health.Configure(team, _health.MaxHealth, _health.MaxShield);
        }

        public void SetArchetype(MechArchetype newArchetype)
        {
            archetype = newArchetype;
            ApplyArchetype();
        }

        public void ApplyArchetype()
        {
            var stats = archetype == MechArchetype.Heavy ? MechStatsPresets.Heavy : MechStatsPresets.Light;
            _movement.Configure(stats);
            _health.Configure(team, stats.MaxHealth, stats.MaxShield);

            if (_primary != null)
            {
                _primary.Configure(archetype == MechArchetype.Heavy ? 45f : 30f);
            }
        }

        private void FixedUpdate()
        {
            if (!_health.IsAlive || _input == null)
            {
                return;
            }

            var input = _input.ReadInput();
            _movement.ApplyInput(input, yawPivot != null ? yawPivot : transform, pitchPivot);

            if (_lockOn != null)
            {
                if (input.LockOnPressed)
                {
                    _lockOn.CycleTarget();
                }
                else if (input.LockOnHeld && _lockOn.CurrentTarget == null)
                {
                    _lockOn.AcquireNearest(FireOrigin);
                }

                _lockOn.UpdateAiming(FireOrigin);
            }

            if (_primary != null && input.FirePrimary)
            {
                _primary.TryFire(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null, gameObject);
            }

            if (_secondary != null && input.FireSecondary)
            {
                _secondary.TryFire(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null, gameObject);
            }
        }

        private void OnDied(HealthSystem _, GameObject killer)
        {
            if (CompareTag("Player"))
            {
                if (GameManager.Instance != null)
                {
                    GameManager.Instance.RegisterDeath();
                }
            }

            gameObject.SetActive(false);
        }
    }
}
