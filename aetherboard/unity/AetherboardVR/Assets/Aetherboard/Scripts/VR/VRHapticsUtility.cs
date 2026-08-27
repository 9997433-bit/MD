using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

namespace Aetherboard.VR
{
    /// <summary>
    /// Cross-platform haptic pulses for Quest / PCVR controllers.
    /// </summary>
    public static class VRHapticsUtility
    {
        public static void PulseLight() => Pulse(0.25f, 0.04f);
        public static void PulseMedium() => Pulse(0.55f, 0.07f);
        public static void PulseStrong() => Pulse(0.9f, 0.12f);
        public static void PulseReject() => Pulse(0.35f, 0.03f);

        public static void Pulse(float amplitude, float durationSeconds)
        {
            amplitude = Mathf.Clamp01(amplitude);
            if (amplitude <= 0f || durationSeconds <= 0f) return;

            var sent = PulseNode(XRNode.RightHand, amplitude, durationSeconds);
            sent |= PulseNode(XRNode.LeftHand, amplitude, durationSeconds);
            if (!sent)
                TryPulseViaXriReflection(amplitude, durationSeconds);
        }

        private static bool PulseNode(XRNode node, float amplitude, float durationSeconds)
        {
            var devices = new List<InputDevice>();
            InputDevices.GetDevicesAtXRNode(node, devices);
            var sent = false;
            foreach (var device in devices)
            {
                if (!device.isValid) continue;
                if (!device.TryGetHapticCapabilities(out var caps) || !caps.supportsImpulse) continue;
                device.SendHapticImpulse(0u, amplitude, durationSeconds);
                sent = true;
            }
            return sent;
        }

        private static void TryPulseViaXriReflection(float amplitude, float durationSeconds)
        {
            var controllerType = System.Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.ActionBasedController, Unity.XR.Interaction.Toolkit");
            if (controllerType == null) return;

            var controllers = Object.FindObjectsOfType(controllerType);
            foreach (var controller in controllers)
            {
                var method = controllerType.GetMethod(
                    "SendHapticImpulse",
                    new[] { typeof(float), typeof(float) });
                method?.Invoke(controller, new object[] { amplitude, durationSeconds });
            }
        }
    }
}
