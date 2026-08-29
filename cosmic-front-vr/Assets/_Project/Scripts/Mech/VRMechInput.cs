using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;
using CosmicFront.Player;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Reads OpenXR / SteamVR controllers via Unity XR InputDevices API.
    /// Left stick = move, right stick = yaw/pitch, triggers = weapons, left grip = lock.
    /// </summary>
    public class VRMechInput : MonoBehaviour, IMechInputProvider
    {
        [SerializeField] private float stickDeadzone = 0.15f;
        [SerializeField] private float yawScale = 1f;
        [SerializeField] private float pitchScale = 1f;

        private bool _lockPressedLastFrame;

        public static bool IsHeadsetPresent()
        {
            var devices = new List<InputDevice>();
            InputDevices.GetDevicesWithCharacteristics(InputDeviceCharacteristics.HeadMounted, devices);
            return devices.Count > 0 && devices[0].isValid;
        }

        public MechInputState ReadInput()
        {
            var left = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
            var right = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);

            ReadStick(left, out var leftStick);
            ReadStick(right, out var rightStick);

            leftStick = ApplyDeadzone(leftStick);
            rightStick = ApplyDeadzone(rightStick);

            ReadButton(left, CommonUsages.primary2DAxisClick, out var leftClick);
            ReadButton(left, CommonUsages.gripButton, out var leftGrip);
            ReadButton(right, CommonUsages.primaryButton, out var rightPrimary);
            ReadButton(right, CommonUsages.secondaryButton, out var rightSecondary);

            ReadAxis(left, CommonUsages.trigger, out var leftTrigger);
            ReadAxis(right, CommonUsages.trigger, out var rightTrigger);

            var lockPressed = leftGrip || rightPrimary;
            var lockOnPressed = lockPressed && !_lockPressedLastFrame;
            _lockPressedLastFrame = lockPressed;

            var moveX = leftStick.x;
            var yaw = rightStick.x * yawScale;
            var comfort = VRComfortSettings.Instance;
            if (comfort != null)
            {
                if (comfort.DisableStrafeOption)
                {
                    moveX = 0f;
                }

                // When snap is off, scale continuous yaw by comfort SmoothTurnSpeed (90°/s baseline).
                if (comfort.SmoothTurnEnabled && comfort.SmoothTurnSpeed > 0f)
                {
                    yaw *= comfort.SmoothTurnSpeed / 90f;
                }
            }

            return new MechInputState
            {
                Move = new Vector3(moveX, 0f, leftStick.y),
                Yaw = yaw,
                Pitch = -rightStick.y * pitchScale,
                Boost = leftClick,
                FirePrimary = rightTrigger > 0.5f,
                FireSecondary = leftTrigger > 0.5f,
                AbilityPressed = rightSecondary,
                LockOnPressed = lockOnPressed,
                LockOnHeld = lockPressed
            };
        }

        private static void ReadStick(InputDevice device, out Vector2 value)
        {
            value = Vector2.zero;
            if (device.isValid)
            {
                device.TryGetFeatureValue(CommonUsages.primary2DAxis, out value);
            }
        }

        private static void ReadAxis(InputDevice device, InputFeatureUsage<float> usage, out float value)
        {
            value = 0f;
            if (device.isValid)
            {
                device.TryGetFeatureValue(usage, out value);
            }
        }

        private static void ReadButton(InputDevice device, InputFeatureUsage<bool> usage, out bool value)
        {
            value = false;
            if (device.isValid)
            {
                device.TryGetFeatureValue(usage, out value);
            }
        }

        private Vector2 ApplyDeadzone(Vector2 v)
        {
            if (v.magnitude < stickDeadzone)
            {
                return Vector2.zero;
            }

            return v.normalized * ((v.magnitude - stickDeadzone) / (1f - stickDeadzone));
        }
    }
}
