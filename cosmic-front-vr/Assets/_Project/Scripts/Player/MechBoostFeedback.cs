using UnityEngine;
using CosmicFront.Mech;

namespace CosmicFront.Player
{
    /// <summary>
    /// Drives boost vignette from mech input state.
    /// </summary>
    public class MechBoostFeedback : MonoBehaviour
    {
        [SerializeField] private MechInputRouter inputRouter;

        private void Awake()
        {
            inputRouter = GetComponent<MechInputRouter>();
        }

        private void Update()
        {
            if (inputRouter == null || VRComfortSettings.Instance == null)
            {
                return;
            }

            VRComfortSettings.Instance.SetBoostVignetteActive(inputRouter.LastInput.Boost);
        }
    }
}
