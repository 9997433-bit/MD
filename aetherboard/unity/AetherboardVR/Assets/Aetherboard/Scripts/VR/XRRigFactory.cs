using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Spawns XR Origin when XRI is available; otherwise positions a desktop camera rig.
    /// </summary>
    public static class XRRigFactory
    {
        public static bool XrActive { get; private set; }

        public static Transform CreateRig(Vector3 tableCenter, bool seated, out Camera camera)
        {
            XrActive = TryCreateXriOrigin(tableCenter, seated, out var rigRoot, out camera);
            if (XrActive) return rigRoot;

            camera = SetupDesktopCamera(tableCenter);
            return camera.transform;
        }

        private static bool TryCreateXriOrigin(Vector3 tableCenter, bool seated, out Transform root, out Camera cam)
        {
            root = null;
            cam = null;

            var originType = System.Type.GetType("Unity.XR.CoreUtils.XROrigin, Unity.XR.CoreUtils");
            if (originType == null) return false;

            var rigGo = new GameObject("XR Origin");
            var origin = rigGo.AddComponent(originType);

            var cameraOffset = new GameObject("Camera Offset").transform;
            cameraOffset.SetParent(rigGo.transform, false);
            cameraOffset.localPosition = seated ? new Vector3(0, 1.35f, 0) : new Vector3(0, 1.65f, 0);

            var camGo = new GameObject("Main Camera");
            camGo.tag = "MainCamera";
            cam = camGo.AddComponent<Camera>();
            cam.nearClipPlane = 0.05f;
            camGo.AddComponent<AudioListener>();
            camGo.transform.SetParent(cameraOffset, false);

            TryAddTrackedPoseDriver(camGo);
            TryAddXriRayInteractor(cameraOffset);

            rigGo.transform.position = tableCenter + new Vector3(0, 0, -0.85f);
            rigGo.transform.LookAt(tableCenter);

            var originCameraProp = originType.GetProperty("Camera");
            originCameraProp?.SetValue(origin, cam);

            root = rigGo.transform;
            return true;
        }

        private static void TryAddTrackedPoseDriver(GameObject camGo)
        {
            var tpdType = System.Type.GetType(
                "UnityEngine.InputSystem.XR.TrackedPoseDriver, Unity.InputSystem");
            if (tpdType == null) return;
            var tpd = camGo.AddComponent(tpdType);
            // Default bindings apply when XR device is present.
        }

        private static void TryAddXriRayInteractor(Transform cameraOffset)
        {
            var rayType = System.Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.Interactors.XRRayInteractor, Unity.XR.Interaction.Toolkit");
            if (rayType == null) return;

            var rightHand = new GameObject("Right Hand Ray");
            rightHand.transform.SetParent(cameraOffset, false);
            rightHand.transform.localPosition = new Vector3(0.15f, -0.05f, 0.3f);
            rightHand.AddComponent(rayType);

            var leftHand = new GameObject("Left Hand Ray");
            leftHand.transform.SetParent(cameraOffset, false);
            leftHand.transform.localPosition = new Vector3(-0.15f, -0.05f, 0.3f);
            leftHand.AddComponent(rayType);
        }

        private static Camera SetupDesktopCamera(Vector3 tableCenter)
        {
            var cam = Camera.main;
            if (cam == null)
            {
                var camGo = new GameObject("Main Camera");
                cam = camGo.AddComponent<Camera>();
                camGo.tag = "MainCamera";
                camGo.AddComponent<AudioListener>();
            }
            cam.transform.position = tableCenter + new Vector3(0, 0.65f, -0.85f);
            cam.transform.LookAt(tableCenter + Vector3.up * 0.05f);
            return cam;
        }

        public static void EnsureLighting()
        {
            if (Object.FindObjectOfType<Light>() != null) return;
            var lightGo = new GameObject("Directional Light");
            var light = lightGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            lightGo.transform.rotation = Quaternion.Euler(50, -30, 0);
        }
    }
}
