using UnityEngine;
using CosmicFront.Mech;

namespace CosmicFront.Player
{
    /// <summary>
    /// Minimal XR camera rig when XRI Starter Assets are not imported yet.
    /// Tracks headset position for view; PlayerMechBinder snaps rig to cockpit.
    /// </summary>
    public class XROriginSetup : MonoBehaviour
    {
        [SerializeField] private Camera vrCamera;
        [SerializeField] private Transform cameraOffset;

        public Camera VrCamera => vrCamera;

        private void Reset()
        {
            EnsureHierarchy();
        }

        private void Awake()
        {
            EnsureHierarchy();
        }

        public void EnsureHierarchy()
        {
            if (cameraOffset == null)
            {
                var offsetGo = transform.Find("CameraOffset");
                if (offsetGo == null)
                {
                    offsetGo = new GameObject("CameraOffset").transform;
                    offsetGo.SetParent(transform, false);
                }

                cameraOffset = offsetGo;
            }

            if (vrCamera == null)
            {
                vrCamera = cameraOffset.GetComponentInChildren<Camera>();
                if (vrCamera == null)
                {
                    var camGo = new GameObject("VRCamera");
                    camGo.transform.SetParent(cameraOffset, false);
                    vrCamera = camGo.AddComponent<Camera>();
                    camGo.AddComponent<AudioListener>();
                    camGo.tag = "MainCamera";
                }
            }

            var main = Camera.main;
            if (main != null && main != vrCamera && main.transform.root == transform.root)
            {
                main.enabled = false;
            }
        }
    }
}
