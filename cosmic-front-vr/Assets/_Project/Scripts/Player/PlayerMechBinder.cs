using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.Player
{
    /// <summary>
    /// Attach to XR Origin. Camera lives inside cockpit; mech moves independently.
    /// </summary>
    public class PlayerMechBinder : MonoBehaviour
    {
        [SerializeField] private MechController mech;
        [SerializeField] private Transform cockpitAnchor;
        [SerializeField] private FallbackMechInput fallbackInput;

        private void LateUpdate()
        {
            if (cockpitAnchor == null)
            {
                return;
            }

            transform.SetPositionAndRotation(cockpitAnchor.position, cockpitAnchor.rotation);
        }

        public void Bind(MechController targetMech, Transform cockpit)
        {
            mech = targetMech;
            cockpitAnchor = cockpit;

            if (fallbackInput == null)
            {
                fallbackInput = mech.gameObject.GetComponent<FallbackMechInput>();
            }

            if (fallbackInput == null && mech != null)
            {
                fallbackInput = mech.gameObject.AddComponent<FallbackMechInput>();
            }
        }
    }
}
