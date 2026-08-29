using UnityEngine;

namespace CosmicFront.Ship
{
    [RequireComponent(typeof(Rigidbody))]
    public class ShipMovement : MonoBehaviour
    {
        [SerializeField] private float maxSpeed = 8f;
        [SerializeField] private float acceleration = 12f;
        [SerializeField] private float verticalSpeed = 5f;
        [SerializeField] private float yawRate = 35f;
        [SerializeField] private float pitchRate = 20f;
        [SerializeField] private float maxPitch = 20f;
        [SerializeField] private float boostMultiplier = 1.4f;
        [SerializeField] private float maxBoostFuel = 80f;
        [SerializeField] private float boostDrain = 18f;
        [SerializeField] private float boostRegen = 10f;

        private Rigidbody _rb;
        private float _pitch;
        private float _boostFuel;

        public float BoostFuelNormalized => maxBoostFuel > 0f ? _boostFuel / maxBoostFuel : 0f;
        public float CurrentSpeed => _rb != null ? _rb.velocity.magnitude : 0f;

        private void Awake()
        {
            _rb = GetComponent<Rigidbody>();
            _rb.useGravity = false;
            _rb.drag = 1.5f;
            _rb.angularDrag = 3f;
            _boostFuel = maxBoostFuel;
        }

        public void ApplyInput(ShipInputState input)
        {
            if (_rb == null)
            {
                return;
            }

            var speedLimit = maxSpeed * (input.Boost && _boostFuel > 0f ? boostMultiplier : 1f);
            var wish = transform.TransformDirection(new Vector3(input.Thrust.x, 0f, input.Thrust.z));
            wish += Vector3.up * input.Thrust.y * (verticalSpeed / Mathf.Max(0.01f, maxSpeed));

            if (wish.sqrMagnitude > 0.001f)
            {
                wish = wish.normalized * speedLimit;
                _rb.velocity = Vector3.MoveTowards(_rb.velocity, wish, acceleration * Time.fixedDeltaTime);
            }

            if (input.Boost && _boostFuel > 0f && _rb.velocity.sqrMagnitude > 0.1f)
            {
                _boostFuel = Mathf.Max(0f, _boostFuel - boostDrain * Time.fixedDeltaTime);
            }
            else if (!input.Boost)
            {
                _boostFuel = Mathf.Min(maxBoostFuel, _boostFuel + boostRegen * Time.fixedDeltaTime);
            }

            transform.Rotate(0f, input.Yaw * yawRate * Time.fixedDeltaTime, 0f, Space.World);
            _pitch = Mathf.Clamp(_pitch + input.Pitch * pitchRate * Time.fixedDeltaTime, -maxPitch, maxPitch);
            var e = transform.eulerAngles;
            transform.rotation = Quaternion.Euler(_pitch, e.y, 0f);
        }
    }
}
