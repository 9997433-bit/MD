using UnityEngine;
using UnityEngine.XR;

namespace CosmicFront.Player
{
    /// <summary>
    /// Snap-turn the XR rig for comfort. Right stick horizontal flick when mech is idle.
    /// </summary>
    public class VRSnapTurn : MonoBehaviour
    {
        [SerializeField] private Transform turnTarget;
        [SerializeField] private float snapThreshold = 0.75f;
        [SerializeField] private float cooldownSeconds = 0.35f;

        private float _cooldown;
        private bool _armed = true;

        private void Update()
        {
            if (!VRComfortSettings.Instance || !VRComfortSettings.Instance.SnapTurnEnabled)
            {
                return;
            }

            if (_cooldown > 0f)
            {
                _cooldown -= Time.deltaTime;
                return;
            }

            var right = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
            if (!right.isValid || !right.TryGetFeatureValue(CommonUsages.primary2DAxis, out var stick))
            {
                return;
            }

            if (Mathf.Abs(stick.x) < snapThreshold)
            {
                _armed = true;
                return;
            }

            if (!_armed)
            {
                return;
            }

            var angle = stick.x > 0f
                ? VRComfortSettings.Instance.SnapTurnAngle
                : -VRComfortSettings.Instance.SnapTurnAngle;

            var target = turnTarget != null ? turnTarget : transform;
            target.Rotate(0f, angle, 0f, Space.World);

            _armed = false;
            _cooldown = cooldownSeconds;
        }
    }
}
