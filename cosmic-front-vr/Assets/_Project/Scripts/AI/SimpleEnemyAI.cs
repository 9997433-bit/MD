using UnityEngine;
using CosmicFront.Mech;

namespace CosmicFront.AI
{
    public enum EnemyState
    {
        Idle,
        Chase,
        Attack,
        Dead
    }

    [RequireComponent(typeof(MechController))]
    public class SimpleEnemyAI : MonoBehaviour, IMechInputProvider
    {
        [SerializeField] private Transform playerTarget;
        [SerializeField] private float detectRange = 120f;
        [SerializeField] private float attackRange = 60f;
        [SerializeField] private float strafeStrength = 0.6f;

        public EnemyState State { get; private set; } = EnemyState.Idle;

        private MechController _mech;
        private bool _lockHeld;
        private float _strafeDir = 1f;
        private float _strafeTimer;

        private void Awake()
        {
            _mech = GetComponent<MechController>();
        }

        private void Start()
        {
            if (playerTarget == null)
            {
                var player = GameObject.FindGameObjectWithTag("Player");
                if (player != null)
                {
                    playerTarget = player.transform;
                }
            }
        }

        public MechInputState ReadInput()
        {
            if (playerTarget == null || State == EnemyState.Dead)
            {
                return default;
            }

            var toPlayer = playerTarget.position - transform.position;
            var flat = new Vector3(toPlayer.x, 0f, toPlayer.z);
            var dist = flat.magnitude;

            if (dist > detectRange)
            {
                State = EnemyState.Idle;
                return default;
            }

            State = dist <= attackRange ? EnemyState.Attack : EnemyState.Chase;

            var localDir = transform.InverseTransformDirection(flat.normalized);
            var move = new Vector3(localDir.x * strafeStrength, 0f, localDir.z);

            _strafeTimer -= Time.deltaTime;
            if (_strafeTimer <= 0f)
            {
                _strafeDir *= -1f;
                _strafeTimer = Random.Range(1.5f, 3f);
            }

            if (State == EnemyState.Attack)
            {
                move.x += _strafeDir * strafeStrength;
            }

            var yaw = Mathf.Clamp(localDir.x * 2f, -1f, 1f);
            _lockHeld = dist <= attackRange;

            return new MechInputState
            {
                Move = Vector3.ClampMagnitude(move, 1f),
                Yaw = yaw,
                Pitch = Mathf.Clamp(-toPlayer.normalized.y, -1f, 1f) * 0.5f,
                Boost = State == EnemyState.Chase,
                FirePrimary = State == EnemyState.Attack,
                FireSecondary = State == EnemyState.Attack && Random.value < 0.01f,
                LockOnHeld = _lockHeld,
                LockOnPressed = false
            };
        }

        public void SetDead()
        {
            State = EnemyState.Dead;
        }
    }
}
