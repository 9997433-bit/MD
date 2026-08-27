using UnityEngine;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Aggregated input for mech control. VR bindings wired in P1 polish; keyboard fallback for Editor.
    /// </summary>
    public struct MechInputState
    {
        public Vector3 Move;
        public float Yaw;
        public float Pitch;
        public bool Boost;
        public bool FirePrimary;
        public bool FireSecondary;
        public bool LockOnPressed;
        public bool LockOnHeld;
    }

    public interface IMechInputProvider
    {
        MechInputState ReadInput();
    }

    public class FallbackMechInput : MonoBehaviour, IMechInputProvider
    {
        [SerializeField] private float yawSpeed = 1f;
        [SerializeField] private float pitchSpeed = 1f;

        public MechInputState ReadInput()
        {
            var move = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical"));
            if (Input.GetKey(KeyCode.R)) move.y += 1f;
            if (Input.GetKey(KeyCode.F)) move.y -= 1f;

            var yaw = 0f;
            if (Input.GetKey(KeyCode.Q)) yaw -= 1f;
            if (Input.GetKey(KeyCode.E)) yaw += 1f;

            return new MechInputState
            {
                Move = Vector3.ClampMagnitude(move, 1f),
                Yaw = yaw * yawSpeed,
                Pitch = (Input.GetKey(KeyCode.T) ? 1f : 0f) + (Input.GetKey(KeyCode.G) ? -1f : 0f),
                Boost = Input.GetKey(KeyCode.LeftShift),
                FirePrimary = Input.GetMouseButton(0),
                FireSecondary = Input.GetMouseButton(1),
                LockOnPressed = Input.GetKeyDown(KeyCode.Tab),
                LockOnHeld = Input.GetKey(KeyCode.Tab)
            };
        }
    }
}
