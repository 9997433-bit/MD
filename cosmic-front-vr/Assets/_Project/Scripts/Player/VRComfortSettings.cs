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
        [SerializeField] private float smoothTurnSpeed = 90f;
        [SerializeField] private bool vignetteOnBoost = true;
        [SerializeField] [Range(0f, 1f)] private float vignetteIntensity = 0.35f;
        [SerializeField] private float seatedModeHeightOffset;
        [SerializeField] private bool disableStrafeOption;
        [SerializeField] private CanvasGroup boostVignette;
        [SerializeField] private Transform seatedHeightTarget;

        public bool SnapTurnEnabled
        {
            get => snapTurnEnabled;
            set => snapTurnEnabled = value;
        }

        /// <summary>True when snap is off — continuous yaw stays with Mech right-stick.</summary>
        public bool SmoothTurnEnabled => !snapTurnEnabled;

        public float SnapTurnAngle => snapTurnAngle;

        public float SmoothTurnSpeed
        {
            get => smoothTurnSpeed;
            set => smoothTurnSpeed = Mathf.Max(0f, value);
        }

        public bool VignetteOnBoost
        {
            get => vignetteOnBoost;
            set => vignetteOnBoost = value;
        }

        public float VignetteIntensity
        {
            get => vignetteIntensity;
            set => vignetteIntensity = Mathf.Clamp01(value);
        }

        public float SeatedModeHeightOffset
        {
            get => seatedModeHeightOffset;
            set
            {
                seatedModeHeightOffset = value;
                ApplySeatedHeightOffset();
            }
        }

        public bool DisableStrafeOption
        {
            get => disableStrafeOption;
            set => disableStrafeOption = value;
        }

        private Vector3 _baseLocalPosition;
        private bool _hasBaseLocalPosition;

        private void Awake()
        {
            Instance = this;
            CacheSeatedTarget();
            ApplySeatedHeightOffset();
        }

        private void OnDestroy()
        {
            if (Instance == this)
            {
                Instance = null;
            }
        }

        public void SetBoostVignetteActive(bool active)
        {
            if (boostVignette != null && vignetteOnBoost)
            {
                boostVignette.alpha = active ? vignetteIntensity : 0f;
            }
        }

        public void ApplySeatedHeightOffset()
        {
            CacheSeatedTarget();
            if (seatedHeightTarget == null)
            {
                return;
            }

            if (!_hasBaseLocalPosition)
            {
                _baseLocalPosition = seatedHeightTarget.localPosition;
                _hasBaseLocalPosition = true;
            }

            var pos = _baseLocalPosition;
            pos.y += seatedModeHeightOffset;
            seatedHeightTarget.localPosition = pos;
        }

        private void CacheSeatedTarget()
        {
            if (seatedHeightTarget != null)
            {
                return;
            }

            var offset = transform.Find("CameraOffset");
            if (offset != null)
            {
                seatedHeightTarget = offset;
            }
        }
    }
}
