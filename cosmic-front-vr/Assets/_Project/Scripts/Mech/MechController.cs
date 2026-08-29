using UnityEngine;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Network;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Root controller for player or AI mechs. Applies target MechModelId stats/visuals/abilities.
    /// </summary>
    [RequireComponent(typeof(MechMovement))]
    [RequireComponent(typeof(HealthSystem))]
    public class MechController : MonoBehaviour
    {
        [SerializeField] private Transform yawPivot;
        [SerializeField] private Transform pitchPivot;
        [SerializeField] private Transform fireOrigin;
        [SerializeField] private MechArchetype archetype = MechArchetype.Light;
        [SerializeField] private MechModelId modelId = MechModelId.Kestrel;
        [SerializeField] private TeamId team = TeamId.Terran;
        [SerializeField] private bool rebuildVisualOnApply = true;

        private MechMovement _movement;
        private HealthSystem _health;
        private LockOnSystem _lockOn;
        private WeaponPrimary _primary;
        private WeaponSecondary _secondary;
        private MechSpecialAbility _ability;
        private IMechInputProvider _input;
        private NetworkMechSync _network;

        public TeamId Team => team;
        public MechArchetype Archetype => archetype;
        public MechModelId ModelId => modelId;
        public LockOnSystem LockOn => _lockOn;
        public Transform FireOrigin => fireOrigin != null ? fireOrigin : pitchPivot;

        private void Awake()
        {
            _movement = GetComponent<MechMovement>();
            _health = GetComponent<HealthSystem>();
            _lockOn = GetComponent<LockOnSystem>();
            _primary = GetComponent<WeaponPrimary>();
            _secondary = GetComponent<WeaponSecondary>();
            _ability = GetComponent<MechSpecialAbility>();
            if (_ability == null)
            {
                _ability = gameObject.AddComponent<MechSpecialAbility>();
            }

            _network = GetComponent<NetworkMechSync>();
            _input = GetComponent<MechInputRouter>() ?? GetComponent<IMechInputProvider>();

            ApplyModel();
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
            if (rebuildVisualOnApply)
            {
                MechVisualBuilder.Apply(transform, modelId, team);
            }
        }

        public void SetArchetype(MechArchetype newArchetype)
        {
            archetype = newArchetype;
            modelId = MechModelCatalog.FromArchetype(newArchetype).Id;
            ApplyModel();
        }

        public void SetModel(MechModelId newModel)
        {
            modelId = newModel;
            archetype = MechModelCatalog.Get(newModel).Archetype;
            ApplyModel();
        }

        public void ApplyArchetype() => ApplyModel();

        public void ApplyModel()
        {
            var def = MechModelCatalog.Get(modelId);
            archetype = def.Archetype;
            var stats = MechModelCatalog.ToStats(def);
            _movement.Configure(stats);
            _health.Configure(team, stats.MaxHealth, stats.MaxShield);

            if (_primary != null)
            {
                _primary.Configure(def.PrimaryDps);
            }

            if (_secondary != null)
            {
                _secondary.ConfigureDamage(def.SecondaryDamage);
            }

            if (_lockOn != null)
            {
                _lockOn.ConfigureSensors(def.LockRange, def.LockCone);
            }

            _ability?.Configure(modelId);

            if (rebuildVisualOnApply)
            {
                MechVisualBuilder.Apply(transform, modelId, team);
            }
        }

        private void FixedUpdate()
        {
            if (!_health.IsAlive || _input == null)
            {
                return;
            }

            if (_network != null && !_network.IsLocalPlayer)
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

            if (input.AbilityPressed && _ability != null)
            {
                _ability.TryActivate(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null);
            }

            if (_primary != null && input.FirePrimary)
            {
                if (_network != null)
                {
                    _network.RequestPrimaryFire(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null);
                }
                else
                {
                    _primary.TryFire(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null, gameObject);
                }
            }

            if (_secondary != null && input.FireSecondary)
            {
                if (_network != null)
                {
                    _network.RequestSecondaryFire(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null);
                }
                else
                {
                    _secondary.TryFire(FireOrigin, _lockOn != null ? _lockOn.CurrentTarget : null, gameObject);
                }
            }
        }

        private void OnDied(HealthSystem _, GameObject killer)
        {
            if (GetComponent<NetworkHealthSync>() != null)
            {
                return;
            }

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
