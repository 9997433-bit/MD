using UnityEngine;
using CosmicFront.Mech;

namespace CosmicFront.Player
{
    /// <summary>
    /// Attach to XR Origin. Camera lives inside cockpit / ship seat; parent moves independently.
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

            if (mech == null)
            {
                return;
            }

            if (fallbackInput == null)
            {
                fallbackInput = mech.gameObject.GetComponent<FallbackMechInput>();
            }

            if (fallbackInput == null)
            {
                fallbackInput = mech.gameObject.AddComponent<FallbackMechInput>();
            }
        }
    }
}
