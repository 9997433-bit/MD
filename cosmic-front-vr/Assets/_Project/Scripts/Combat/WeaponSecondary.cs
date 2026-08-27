using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Combat
{
    public class WeaponSecondary : MonoBehaviour
    {
        [SerializeField] private GameObject projectilePrefab;
        [SerializeField] private float fireCooldown = 1.2f;
        [SerializeField] private int maxAmmo = 4;
        [SerializeField] private float reloadTime = 4f;
        [SerializeField] private float projectileSpeed = 40f;
        [SerializeField] private float projectileDamage = 25f;

        private float _cooldown;
        private int _ammo;
        private float _reloadTimer;

        private void Awake()
        {
            _ammo = maxAmmo;
        }

        public void TryFire(Transform origin, Transform lockTarget, GameObject owner)
        {
            if (origin == null || _cooldown > 0f || _reloadTimer > 0f || _ammo <= 0)
            {
                return;
            }

            _cooldown = fireCooldown;
            _ammo--;

            if (_ammo <= 0)
            {
                _reloadTimer = reloadTime;
            }

            if (projectilePrefab == null)
            {
                FireFallback(origin, lockTarget, owner);
                return;
            }

            var go = Instantiate(projectilePrefab, origin.position, origin.rotation);
            var proj = go.GetComponent<Projectile>();
            if (proj != null)
            {
                var dir = lockTarget != null
                    ? (lockTarget.position - origin.position).normalized
                    : origin.forward;
                proj.Initialize(owner, dir, projectileSpeed, projectileDamage);
            }
        }

        private void FireFallback(Transform origin, Transform lockTarget, GameObject owner)
        {
            var dir = lockTarget != null
                ? (lockTarget.position - origin.position).normalized
                : origin.forward;

            if (Physics.Raycast(origin.position, dir, out var hit, 120f, ~0, QueryTriggerInteraction.Ignore))
            {
                var damageable = hit.collider.GetComponentInParent<IDamageable>();
                if (damageable != null)
                {
                    damageable.ApplyDamage(projectileDamage, owner);
                }
            }
        }

        private void Update()
        {
            if (_cooldown > 0f) _cooldown -= Time.deltaTime;
            if (_reloadTimer > 0f)
            {
                _reloadTimer -= Time.deltaTime;
                if (_reloadTimer <= 0f) _ammo = maxAmmo;
            }
        }
    }
}
