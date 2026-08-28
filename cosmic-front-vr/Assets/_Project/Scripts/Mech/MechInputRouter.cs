using UnityEngine;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Auto-selects VR or keyboard input. Attach alongside VRMechInput + FallbackMechInput on player mechs.
    /// </summary>
    [RequireComponent(typeof(FallbackMechInput))]
    public class MechInputRouter : MonoBehaviour, IMechInputProvider
    {
        [SerializeField] private bool preferVrWhenPresent = true;

        private VRMechInput _vrInput;
        private FallbackMechInput _fallbackInput;

        public bool UsingVr { get; private set; }
        public MechInputState LastInput { get; private set; }

        private void Awake()
        {
            _vrInput = GetComponent<VRMechInput>();
            _fallbackInput = GetComponent<FallbackMechInput>();

            if (_vrInput == null)
            {
                _vrInput = gameObject.AddComponent<VRMechInput>();
            }
        }

        public MechInputState ReadInput()
        {
            UsingVr = preferVrWhenPresent && VRMechInput.IsHeadsetPresent();
            LastInput = UsingVr && _vrInput != null
                ? _vrInput.ReadInput()
                : _fallbackInput != null ? _fallbackInput.ReadInput() : default;
            return LastInput;
        }
    }
}
