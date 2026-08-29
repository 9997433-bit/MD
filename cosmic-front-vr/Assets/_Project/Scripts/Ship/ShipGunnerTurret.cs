using UnityEngine;
using CosmicFront.Combat;
using CosmicFront.Core;

namespace CosmicFront.Ship
{
    /// <summary>
    /// Manual gunner turret. Aim with yaw/pitch input, fire with trigger.
    /// </summary>
    public class ShipGunnerTurret : MonoBehaviour
    {
        [SerializeField] private Transform yawPivot;
        [SerializeField] private Transform pitchPivot;
        [SerializeField] private Transform fireOrigin;
        [SerializeField] private float yawRate = 80f;
        [SerializeField] private float pitchRate = 60f;
        [SerializeField] private float minPitch = -20f;
        [SerializeField] private float maxPitch = 40f;
        [SerializeField] private float fireRate = 4f;
        [SerializeField] private float damage = 18f;
        [SerializeField] private float range = 220f;
        [SerializeField] private TeamId team = TeamId.Terran;

        private float _pitch;
        private float _cooldown;

        public void SetTeam(TeamId newTeam)
        {
            team = newTeam;
        }

        public void ApplyAim(float yawInput, float pitchInput)
        {
            if (yawPivot != null)
            {
                yawPivot.Rotate(0f, yawInput * yawRate * Time.deltaTime, 0f, Space.Self);
            }

            _pitch = Mathf.Clamp(_pitch + pitchInput * pitchRate * Time.deltaTime, minPitch, maxPitch);
            if (pitchPivot != null)
            {
                pitchPivot.localRotation = Quaternion.Euler(_pitch, 0f, 0f);
            }
        }

        public void TryFire(GameObject owner)
        {
            if (_cooldown > 0f)
            {
                return;
            }

            var origin = fireOrigin != null ? fireOrigin : (pitchPivot != null ? pitchPivot : transform);
            _cooldown = 1f / fireRate;

            if (Physics.Raycast(origin.position, origin.forward, out var hit, range, ~0, QueryTriggerInteraction.Ignore))
            {
                var damageable = hit.collider.GetComponentInParent<IDamageable>();
                if (damageable != null && damageable.IsAlive &&
                    (damageable.Team == TeamId.None || damageable.Team != team))
                {
                    damageable.ApplyDamage(damage, owner);
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
