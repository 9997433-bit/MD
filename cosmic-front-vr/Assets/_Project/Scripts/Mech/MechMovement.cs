using UnityEngine;
using CosmicFront.Mech;

namespace CosmicFront.Mech
{
    [RequireComponent(typeof(Rigidbody))]
    public class MechMovement : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float maxSpeed = 18f;
        [SerializeField] private float acceleration = 35f;
        [SerializeField] private float verticalSpeed = 12f;
        [SerializeField] private float boostMultiplier = 1.8f;
        [SerializeField] private float drag = 2f;

        [Header("Rotation")]
        [SerializeField] private float yawRate = 90f;
        [SerializeField] private float pitchRate = 45f;
        [SerializeField] private float maxPitch = 30f;

        [Header("Boost")]
        [SerializeField] private float maxBoostFuel = 100f;
        [SerializeField] private float boostDrainPerSecond = 25f;
        [SerializeField] private float boostRegenPerSecond = 15f;

        public float BoostFuelNormalized => maxBoostFuel > 0f ? BoostFuel / maxBoostFuel : 0f;
        public float CurrentSpeed => _rb.velocity.magnitude;

        private Rigidbody _rb;
        private float _pitch;
        private float _boostFuel;

        public float BoostFuel
        {
            get => _boostFuel;
            private set => _boostFuel = Mathf.Clamp(value, 0f, maxBoostFuel);
        }

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.useGravity = false;
            _rb.drag = drag;
            _rb.angularDrag = 4f;
            _boostFuel = maxBoostFuel;
        }

        public void Configure(MechStats stats)
        {
            maxSpeed = stats.MaxSpeed;
            maxBoostFuel = stats.BoostFuel;
            BoostFuel = stats.BoostFuel;
        }

        public void ApplyInput(MechInputState input, Transform yawPivot, Transform pitchPivot)
        {
            var speedLimit = maxSpeed * (input.Boost && BoostFuel > 0f ? boostMultiplier : 1f);
            var wish = transform.TransformDirection(new Vector3(input.Move.x, 0f, input.Move.z));
            wish += Vector3.up * input.Move.y * (verticalSpeed / maxSpeed);

            if (wish.sqrMagnitude > 0.001f)
            {
                wish = wish.normalized * speedLimit;
                _rb.velocity = Vector3.MoveTowards(_rb.velocity, wish, acceleration * Time.fixedDeltaTime);
            }

            if (input.Boost && BoostFuel > 0f && _rb.velocity.sqrMagnitude > 0.1f)
            {
                BoostFuel -= boostDrainPerSecond * Time.fixedDeltaTime;
            }
            else if (!input.Boost)
            {
                BoostFuel += boostRegenPerSecond * Time.fixedDeltaTime;
            }

            if (yawPivot != null)
            {
                yawPivot.Rotate(0f, input.Yaw * yawRate * Time.fixedDeltaTime, 0f, Space.Self);
            }

            _pitch = Mathf.Clamp(_pitch + input.Pitch * pitchRate * Time.fixedDeltaTime, -maxPitch, maxPitch);
            if (pitchPivot != null)
            {
                pitchPivot.localRotation = Quaternion.Euler(_pitch, 0f, 0f);
            }
        }
    }

    public struct MechStats
    {
        public float MaxSpeed;
        public float BoostFuel;
        public float MaxHealth;
        public float MaxShield;
    }

    public static class MechStatsPresets
    {
        public static MechStats Light => new MechStats
        {
            MaxSpeed = 18f,
            BoostFuel = 100f,
            MaxHealth = 100f,
            MaxShield = 50f
        };

        public static MechStats Heavy => new MechStats
        {
            MaxSpeed = 12f,
            BoostFuel = 70f,
            MaxHealth = 200f,
            MaxShield = 80f
        };
    }
}
