using UnityEngine;

namespace CosmicFront.Player
{
    /// <summary>
    /// VR comfort options applied to cockpit / camera rig.
    /// </summary>
    public class VRComfortSettings : MonoBehaviour
    {
        public static VRComfortSettings Instance { get; private set; }

        [SerializeField] private bool snapTurnEnabled = true;
        [SerializeField] private float snapTurnAngle = 45f;
        [SerializeField] private bool vignetteOnBoost = true;
        [SerializeField] private CanvasGroup boostVignette;

        public bool SnapTurnEnabled
        {
            get => snapTurnEnabled;
            set => snapTurnEnabled = value;
        }

        public float SnapTurnAngle => snapTurnAngle;

        private void Awake()
        {
            Instance = this;
        }

        public void SetBoostVignetteActive(bool active)
        {
            if (boostVignette != null && vignetteOnBoost)
            {
                boostVignette.alpha = active ? 0.35f : 0f;
            }
        }
    }
}
