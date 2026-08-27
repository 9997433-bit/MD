using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Combat
{
    [RequireComponent(typeof(Rigidbody))]
    public class Projectile : MonoBehaviour
    {
        [SerializeField] private float lifetime = 5f;
        [SerializeField] private float homingTurnRate = 90f;
        [SerializeField] private LayerMask hitMask = ~0;

        private GameObject _owner;
        private Vector3 _direction;
        private float _speed;
        private float _damage;
        private Rigidbody _rb;
        private Transform _homingTarget;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.useGravity = false;
        }

        public void Initialize(GameObject owner, Vector3 direction, float speed, float damage, Transform homingTarget = null)
        {
            _owner = owner;
            _direction = direction.normalized;
            _speed = speed;
            _damage = damage;
            _homingTarget = homingTarget;
            _rb.velocity = _direction * _speed;
            Destroy(gameObject, lifetime);
        }

        private void FixedUpdate()
        {
            if (_homingTarget != null)
            {
                var to = (_homingTarget.position - transform.position).normalized;
                _direction = Vector3.RotateTowards(_direction, to, homingTurnRate * Mathf.Deg2Rad * Time.fixedDeltaTime, 0f);
            }

            _rb.velocity = _direction * _speed;
            transform.rotation = Quaternion.LookRotation(_direction);
        }

        private void OnTriggerEnter(Collider other)
        {
            if (_owner != null && other.transform.IsChildOf(_owner.transform))
            {
                return;
            }

            var damageable = other.GetComponentInParent<IDamageable>();
            if (damageable != null && damageable.IsAlive)
            {
                var ownerTeam = _owner != null ? _owner.GetComponentInParent<IDamageable>() : null;
                if (ownerTeam == null || damageable.Team != ownerTeam.Team || damageable.Team == TeamId.None)
                {
                    damageable.ApplyDamage(_damage, _owner);
                }
            }

            Destroy(gameObject);
        }
    }
}
