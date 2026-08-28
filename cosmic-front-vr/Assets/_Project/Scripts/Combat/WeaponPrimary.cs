using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Combat
{
    public class WeaponPrimary : MonoBehaviour
    {
        [SerializeField] private float fireRate = 8f;
        [SerializeField] private float damage = 8f;
        [SerializeField] private float range = 150f;
        [SerializeField] private float homingAssist = 0.15f;
        [SerializeField] private LayerMask hitMask = ~0;

        private float _dps;
        private float _cooldown;

        public void Configure(float dps)
        {
            _dps = dps;
            damage = dps / fireRate;
        }

        public void TryFire(Transform origin, Transform lockTarget, GameObject owner)
        {
            if (origin == null || _cooldown > 0f)
            {
                return;
            }

            _cooldown = 1f / fireRate;
            var direction = origin.forward;

            if (lockTarget != null && homingAssist > 0f)
            {
                var toTarget = (lockTarget.position - origin.position).normalized;
                direction = Vector3.Slerp(direction, toTarget, homingAssist).normalized;
            }

            MuzzleFlash.Play(origin);
            Debug.DrawRay(origin.position, direction * range, Color.yellow, 0.05f);

            if (Physics.Raycast(origin.position, direction, out var hit, range, hitMask, QueryTriggerInteraction.Ignore))
            {
                HitFeedback.Spawn(hit.point);

                var damageable = hit.collider.GetComponentInParent<IDamageable>();
                if (damageable != null && damageable.IsAlive)
                {
                    var ownerTeam = owner.GetComponentInParent<IDamageable>();
                    if (ownerTeam == null || damageable.Team != ownerTeam.Team || damageable.Team == TeamId.None)
                    {
                        damageable.ApplyDamage(damage, owner);
                        DamageNumberUI.Spawn(hit.point, damage);
                    }
                }
            }
        }

        private void Update()
        {
            if (_cooldown > 0f)
            {
                _cooldown -= Time.deltaTime;
            }
        }
    }
}
