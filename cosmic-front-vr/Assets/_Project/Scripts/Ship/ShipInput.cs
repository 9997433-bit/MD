using UnityEngine;
using CosmicFront.Mech;

namespace CosmicFront.Ship
{
    public struct ShipInputState
    {
        public Vector3 Thrust;
        public float Yaw;
        public float Pitch;
        public bool Boost;
        public bool FireTurret;
        public bool UseCaptainAbility;
        public bool RequestLaunch;
        public bool ExitSeat;
    }

    public interface IShipSeatInputProvider
    {
        ShipInputState ReadShipInput();
    }

    public class FallbackShipInput : MonoBehaviour, IShipSeatInputProvider
    {
        public ShipInputState ReadShipInput()
        {
            var thrust = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical"));
            if (Input.GetKey(KeyCode.R)) thrust.y += 1f;
            if (Input.GetKey(KeyCode.F)) thrust.y -= 1f;

            var yaw = 0f;
            if (Input.GetKey(KeyCode.Q)) yaw -= 1f;
            if (Input.GetKey(KeyCode.E)) yaw += 1f;

            return new ShipInputState
            {
                Thrust = Vector3.ClampMagnitude(thrust, 1f),
                Yaw = yaw,
                Pitch = (Input.GetKey(KeyCode.T) ? 1f : 0f) + (Input.GetKey(KeyCode.G) ? -1f : 0f),
                Boost = Input.GetKey(KeyCode.LeftShift),
                FireTurret = Input.GetMouseButton(0),
                UseCaptainAbility = Input.GetKeyDown(KeyCode.V),
                RequestLaunch = Input.GetKeyDown(KeyCode.L),
                ExitSeat = Input.GetKeyDown(KeyCode.X)
            };
        }
    }

    /// <summary>
    /// Maps VR / keyboard mech input into ship seat actions.
    /// </summary>
    public class ShipSeatInputBridge : MonoBehaviour, IShipSeatInputProvider
    {
        [SerializeField] private bool preferVr;

        private FallbackShipInput _fallback;
        private VRMechInput _vr;

        private void Awake()
        {
            _fallback = GetComponent<FallbackShipInput>();
            if (_fallback == null)
            {
                _fallback = gameObject.AddComponent<FallbackShipInput>();
            }

            _vr = GetComponent<VRMechInput>();
        }

        public ShipInputState ReadShipInput()
        {
            if (preferVr && VRMechInput.IsHeadsetPresent() && _vr != null)
            {
                var m = _vr.ReadInput();
                return new ShipInputState
                {
                    Thrust = m.Move,
                    Yaw = m.Yaw,
                    Pitch = m.Pitch,
                    Boost = m.Boost,
                    FireTurret = m.FirePrimary,
                    UseCaptainAbility = m.FireSecondary,
                    RequestLaunch = m.LockOnPressed,
                    ExitSeat = m.LockOnHeld && m.Boost
                };
            }

            return _fallback.ReadShipInput();
        }
    }
}
