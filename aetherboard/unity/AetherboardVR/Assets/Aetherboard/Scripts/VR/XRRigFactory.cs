using System;
using UnityEngine;
using Object = UnityEngine.Object;

namespace Aetherboard.VR
{
    public enum XRRigSource
    {
        Auto,
        Prefab,
        Procedural
    }

    /// <summary>
    /// Spawns XR Origin from official prefab (Resources) or procedural fallback.
    /// </summary>
    public static class XRRigFactory
    {
        public const string PrefabResourcePath = "Aetherboard/XROriginRig";

        public static bool XrActive { get; private set; }
        public static XRRigSource LastRigSource { get; private set; } = XRRigSource.Procedural;

        public static Transform CreateRig(
            Vector3 tableCenter,
            bool seated,
            out Camera camera,
            XRRigSource source = XRRigSource.Auto)
        {
            XrActive = false;
            camera = null;

            if (source != XRRigSource.Procedural && TryCreatePrefabRig(tableCenter, seated, out var prefabRoot, out camera))
            {
                XrActive = true;
                LastRigSource = XRRigSource.Prefab;
                return prefabRoot;
            }

            if (source == XRRigSource.Prefab)
            {
                Debug.LogWarning(
                    $"[Aetherboard] XR prefab not found at Resources/{PrefabResourcePath}. " +
                    "Run menu Aetherboard → Install XR Origin Prefab, or switch to Auto.");
                camera = SetupDesktopCamera(tableCenter);
                LastRigSource = XRRigSource.Procedural;
                return camera.transform;
            }

            XrActive = TryCreateXriOrigin(tableCenter, seated, out var rigRoot, out camera);
            LastRigSource = XRRigSource.Procedural;
            if (XrActive) return rigRoot;

            camera = SetupDesktopCamera(tableCenter);
            return camera.transform;
        }

        private static bool TryCreatePrefabRig(
            Vector3 tableCenter,
            bool seated,
            out Transform root,
            out Camera cam)
        {
            root = null;
            cam = null;

            var prefab = Resources.Load<GameObject>(PrefabResourcePath);
            if (prefab == null) return false;

            var instance = Object.Instantiate(prefab);
            instance.name = "XR Origin (Prefab)";
            PositionRig(instance.transform, tableCenter, seated);

            cam = instance.GetComponentInChildren<Camera>();
            if (cam == null)
            {
                Object.Destroy(instance);
                return false;
            }

            if (cam.tag != "MainCamera") cam.tag = "MainCamera";
            if (cam.GetComponent<AudioListener>() == null)
                cam.gameObject.AddComponent<AudioListener>();

            TryBindXrOriginCamera(instance, cam);
            TryEnsureInteractionManager();
            root = instance.transform;
            Debug.Log($"[Aetherboard] XR rig loaded from Resources/{PrefabResourcePath}");
            return true;
        }

        private static void PositionRig(Transform rig, Vector3 tableCenter, bool seated)
        {
            var eyeHeight = seated ? 1.35f : 1.65f;
            rig.position = tableCenter + new Vector3(0, eyeHeight, -0.85f);
            rig.LookAt(tableCenter + Vector3.up * 0.05f);
        }

        private static void TryBindXrOriginCamera(GameObject rigRoot, Camera cam)
        {
            var originType = Type.GetType("Unity.XR.CoreUtils.XROrigin, Unity.XR.CoreUtils");
            if (originType == null) return;
            var origin = rigRoot.GetComponent(originType);
            if (origin == null) return;
            originType.GetProperty("Camera")?.SetValue(origin, cam);
        }

        private static void TryEnsureInteractionManager()
        {
            var managerType = Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.XRInteractionManager, Unity.XR.Interaction.Toolkit");
            if (managerType == null) return;
            if (Object.FindObjectOfType(managerType) != null) return;

            var go = new GameObject("XR Interaction Manager");
            go.AddComponent(managerType);
        }

        private static bool TryCreateXriOrigin(Vector3 tableCenter, bool seated, out Transform root, out Camera cam)
        {
            root = null;
            cam = null;

            var originType = Type.GetType("Unity.XR.CoreUtils.XROrigin, Unity.XR.CoreUtils");
            if (originType == null) return false;

            var rigGo = new GameObject("XR Origin (Procedural)");
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
            TryEnsureInteractionManager();

            PositionRig(rigGo.transform, tableCenter, seated);

            originType.GetProperty("Camera")?.SetValue(origin, cam);

            root = rigGo.transform;
            return true;
        }

        private static void TryAddTrackedPoseDriver(GameObject camGo)
        {
            var tpdType = Type.GetType(
                "UnityEngine.InputSystem.XR.TrackedPoseDriver, Unity.InputSystem");
            if (tpdType == null) return;
            camGo.AddComponent(tpdType);
        }

        private static void TryAddXriRayInteractor(Transform cameraOffset)
        {
            var rayType = Type.GetType(
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
