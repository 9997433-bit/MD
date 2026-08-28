using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.AI
{
    public enum NeutralSupportState
    {
        Idle,
        Follow,
        Support,
        Dead
    }

    /// <summary>
    /// Peacekeeper support AI: follows allies, heals / restores shield in range,
    /// never initiates fire on the player.
    /// </summary>
    [RequireComponent(typeof(MechController))]
    public class NeutralSupportAI : MonoBehaviour, IMechInputProvider
    {
        [SerializeField] private Transform allyTarget;
        [SerializeField] private float detectRange = 140f;
        [SerializeField] private float followDistance = 18f;
        [SerializeField] private float supportRange = 28f;
        [SerializeField] private float healPerSecond = 12f;
        [SerializeField] private float shieldPerSecond = 8f;
        [SerializeField] private float retargetInterval = 1.5f;

        public NeutralSupportState State { get; private set; } = NeutralSupportState.Idle;

        private MechController _mech;
        private HealthSystem _selfHealth;
        private HealthSystem _allyHealth;
        private float _retargetTimer;

        private void Awake()
        {
            _mech = GetComponent<MechController>();
            _selfHealth = GetComponent<HealthSystem>();
        }

        private void Start()
        {
            ResolveAlly(force: true);
        }

        public MechInputState ReadInput()
        {
            if (State == NeutralSupportState.Dead ||
                (_selfHealth != null && !_selfHealth.IsAlive))
            {
                State = NeutralSupportState.Dead;
                return default;
            }

            _retargetTimer -= Time.deltaTime;
            if (_retargetTimer <= 0f || !IsValidAlly(_allyHealth))
            {
                ResolveAlly(force: false);
                _retargetTimer = retargetInterval;
            }

            if (!IsValidAlly(_allyHealth))
            {
                State = NeutralSupportState.Idle;
                return default;
            }

            var toAlly = _allyHealth.transform.position - transform.position;
            var dist = toAlly.magnitude;

            if (dist > detectRange)
            {
                State = NeutralSupportState.Idle;
                return default;
            }

            if (dist <= supportRange)
            {
                State = NeutralSupportState.Support;
                ApplySupport(Time.deltaTime);
            }
            else
            {
                State = NeutralSupportState.Follow;
            }

            // Hold formation offset — approach until followDistance, then hover.
            var desired = Mathf.Max(0f, dist - followDistance);
            var localDir = transform.InverseTransformDirection(toAlly.normalized);
            var move = State == NeutralSupportState.Follow
                ? new Vector3(localDir.x * 0.4f, 0f, Mathf.Clamp(desired / followDistance, 0f, 1f))
                : new Vector3(localDir.x * 0.2f, 0f, 0f);

            var yaw = Mathf.Clamp(localDir.x * 1.5f, -1f, 1f);

            // Never fire on the player (or anyone) — support-only posture.
            return new MechInputState
            {
                Move = Vector3.ClampMagnitude(move, 1f),
                Yaw = yaw,
                Pitch = Mathf.Clamp(-toAlly.normalized.y, -1f, 1f) * 0.35f,
                Boost = State == NeutralSupportState.Follow && dist > followDistance * 2f,
                FirePrimary = false,
                FireSecondary = false,
                LockOnHeld = false,
                LockOnPressed = false
            };
        }

        public void SetDead()
        {
            State = NeutralSupportState.Dead;
        }

        public void SetAlly(Transform ally)
        {
            allyTarget = ally;
            _allyHealth = ally != null ? ally.GetComponentInParent<HealthSystem>() : null;
        }

        private void ApplySupport(float dt)
        {
            if (_allyHealth == null || !_allyHealth.IsAlive)
            {
                return;
            }

            if (_allyHealth.CurrentHealth < _allyHealth.MaxHealth)
            {
                _allyHealth.Heal(healPerSecond * dt);
            }
            else if (_allyHealth.CurrentShield < _allyHealth.MaxShield)
            {
                _allyHealth.RestoreShield(shieldPerSecond * dt);
            }
        }

        private void ResolveAlly(bool force)
        {
            if (!force && IsValidAlly(_allyHealth))
            {
                return;
            }

            if (allyTarget != null)
            {
                _allyHealth = allyTarget.GetComponentInParent<HealthSystem>();
                if (IsValidAlly(_allyHealth))
                {
                    return;
                }
            }

            _allyHealth = null;
            var bestDist = float.MaxValue;
            var selfTeam = _selfHealth != null ? _selfHealth.Team : TeamId.Neutral;

            foreach (var health in FindObjectsOfType<HealthSystem>())
            {
                if (!IsCandidateAlly(health, selfTeam))
                {
                    continue;
                }

                var d = Vector3.Distance(transform.position, health.transform.position);
                if (d < bestDist)
                {
                    bestDist = d;
                    _allyHealth = health;
                }
            }
        }

        private bool IsCandidateAlly(HealthSystem health, TeamId selfTeam)
        {
            if (!IsValidAlly(health))
            {
                return false;
            }

            // Prefer same team; Neutral may also escort player-tagged units.
            if (health.Team == selfTeam)
            {
                return true;
            }

            return health.CompareTag("Player");
        }

        private bool IsValidAlly(HealthSystem health)
        {
            return health != null &&
                   health != _selfHealth &&
                   health.IsAlive &&
                   health.gameObject != gameObject;
        }
    }
}
