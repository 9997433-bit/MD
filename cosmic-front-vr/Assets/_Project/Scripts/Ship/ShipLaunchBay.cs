using System;
using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.Ship
{
    /// <summary>
    /// Launch bay that ejects a mech into battle from the ship.
    /// </summary>
    public class ShipLaunchBay : MonoBehaviour
    {
        [SerializeField] private Transform launchPoint;
        [SerializeField] private GameObject mechPrefab;
        [SerializeField] private float launchImpulse = 25f;
        [SerializeField] private float cooldownSeconds = 8f;

        private float _cooldown;
        private ShipController _ship;

        public float CooldownNormalized => cooldownSeconds > 0f ? 1f - Mathf.Clamp01(_cooldown / cooldownSeconds) : 1f;
        public bool Ready => _cooldown <= 0f;

        public event Action<GameObject> MechLaunched;

        public void Bind(ShipController ship)
        {
            _ship = ship;
        }

        public GameObject TryLaunch(TeamId team, MechArchetype archetype, GameObject owner)
        {
            if (!Ready || mechPrefab == null)
            {
                return null;
            }

            var point = launchPoint != null ? launchPoint : transform;
            var mech = Instantiate(mechPrefab, point.position, point.rotation);
            var controller = mech.GetComponent<MechController>();
            if (controller != null)
            {
                controller.SetTeam(team);
                controller.SetArchetype(archetype);
            }

            var rb = mech.GetComponent<Rigidbody>();
            if (rb != null)
            {
                rb.velocity = point.forward * launchImpulse;
            }

            _cooldown = cooldownSeconds;
            MechLaunched?.Invoke(mech);
            return mech;
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
