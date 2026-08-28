using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Model-specific special abilities. Secondary fire / ability key triggers when available.
    /// </summary>
    public class MechSpecialAbility : MonoBehaviour
    {
        [SerializeField] private float cooldown = 12f;

        private MechController _mech;
        private MechModelId _modelId;
        private float _cd;
        private float _activeTimer;
        private string _abilityId = "none";

        public float CooldownNormalized => cooldown > 0f ? 1f - Mathf.Clamp01(_cd / cooldown) : 1f;
        public bool IsReady => _cd <= 0f && _activeTimer <= 0f;
        public string AbilityId => _abilityId;

        private void Awake()
        {
            _mech = GetComponent<MechController>();
        }

        public void Configure(MechModelId modelId)
        {
            _modelId = modelId;
            var def = MechModelCatalog.Get(modelId);
            _abilityId = def.AbilityId;
            cooldown = modelId switch
            {
                MechModelId.Warden => 8f,
                MechModelId.Mediator => 14f,
                MechModelId.Beacon => 10f,
                MechModelId.Bastion => 16f,
                _ => 12f
            };
            _cd = 0f;
        }

        public bool TryActivate(Transform aimOrigin, Transform lockTarget)
        {
            if (!IsReady || _mech == null)
            {
                return false;
            }

            var ok = _modelId switch
            {
                MechModelId.Warden => ActivateRepairBeam(lockTarget),
                MechModelId.Mediator => ActivatePhaseProjector(),
                MechModelId.Beacon => ActivateSensorPing(),
                MechModelId.Bastion => ActivateHeavyBurst(aimOrigin, lockTarget),
                MechModelId.Kestrel => ActivateBoostDash(),
                _ => false
            };

            if (ok)
            {
                _cd = cooldown;
            }

            return ok;
        }

        private bool ActivateRepairBeam(Transform lockTarget)
        {
            var targetHealth = ResolveFriendly(lockTarget);
            if (targetHealth == null)
            {
                // Heal self lightly if no ally locked.
                var self = GetComponent<HealthSystem>();
                self?.Heal(25f);
                self?.RestoreShield(20f);
                Debug.Log("[Ability] Warden self-repair");
                return true;
            }

            targetHealth.Heal(40f);
            targetHealth.RestoreShield(30f);
            Debug.Log($"[Ability] Warden repair → {targetHealth.name}");
            return true;
        }

        private bool ActivatePhaseProjector()
        {
            var self = GetComponent<HealthSystem>();
            if (self == null)
            {
                return false;
            }

            self.RestoreShield(60f);
            _activeTimer = 5f;
            Debug.Log("[Ability] Mediator phase projector");
            return true;
        }

        private bool ActivateSensorPing()
        {
            var lockOn = GetComponent<Combat.LockOnSystem>();
            if (lockOn != null)
            {
                lockOn.AcquireNearest(_mech.FireOrigin);
            }

            // Temporarily widen sensors via reconfigure pattern: store and restore.
            _activeTimer = 6f;
            Debug.Log("[Ability] Beacon sensor ping — lock refreshed, range boosted window");
            return true;
        }

        private bool ActivateHeavyBurst(Transform origin, Transform lockTarget)
        {
            var primary = GetComponent<Combat.WeaponPrimary>();
            if (primary == null || origin == null)
            {
                return false;
            }

            for (var i = 0; i < 3; i++)
            {
                primary.TryFire(origin, lockTarget, gameObject);
            }

            Debug.Log("[Ability] Bastion heavy burst");
            return true;
        }

        private bool ActivateBoostDash()
        {
            var rb = GetComponent<Rigidbody>();
            if (rb == null)
            {
                return false;
            }

            rb.velocity += transform.forward * 22f;
            Debug.Log("[Ability] Kestrel boost dash");
            return true;
        }

        private HealthSystem ResolveFriendly(Transform lockTarget)
        {
            if (lockTarget == null)
            {
                return FindNearestAlly();
            }

            var h = lockTarget.GetComponentInParent<HealthSystem>();
            if (h != null && h.IsAlive && h.Team == _mech.Team && h.gameObject != gameObject)
            {
                return h;
            }

            return FindNearestAlly();
        }

        private HealthSystem FindNearestAlly()
        {
            HealthSystem best = null;
            var bestDist = 40f;
            foreach (var h in FindObjectsOfType<HealthSystem>())
            {
                if (!h.IsAlive || h.Team != _mech.Team || h.gameObject == gameObject)
                {
                    continue;
                }

                var d = Vector3.Distance(transform.position, h.transform.position);
                if (d < bestDist)
                {
                    bestDist = d;
                    best = h;
                }
            }

            return best;
        }

        private void Update()
        {
            if (_cd > 0f)
            {
                _cd -= Time.deltaTime;
            }

            if (_activeTimer > 0f)
            {
                _activeTimer -= Time.deltaTime;
            }
        }
    }
}
