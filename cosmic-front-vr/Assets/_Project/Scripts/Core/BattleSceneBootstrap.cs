using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Player;
using CosmicFront.UI;

namespace CosmicFront.Core
{
    /// <summary>
    /// Place in battle scene: wires player mech, HUD, and notifies GameManager.
    /// </summary>
    public class BattleSceneBootstrap : MonoBehaviour
    {
        [SerializeField] private MechController playerMech;
        [SerializeField] private PlayerMechBinder playerBinder;
        [SerializeField] private CockpitHUD cockpitHud;
        [SerializeField] private Camera fallbackCamera;

        private void Start()
        {
            if (GameManager.Instance != null)
            {
                ApplyLoadoutFromGameManager();
                GameManager.Instance.OnBattleSceneLoaded();
            }

            if (playerMech != null)
            {
                var cockpit = playerMech.transform.Find("CockpitAnchor");
                if (cockpit == null)
                {
                    cockpit = playerMech.transform;
                }

                if (playerBinder != null)
                {
                    playerBinder.Bind(playerMech, cockpit);
                }

                if (cockpitHud != null)
                {
                    cockpitHud.Bind(playerMech);
                }

                if (fallbackCamera != null)
                {
                    fallbackCamera.transform.SetParent(cockpit, false);
                }
            }
        }

        private void ApplyLoadoutFromGameManager()
        {
            if (playerMech == null || GameManager.Instance == null)
            {
                return;
            }

            playerMech.SetTeam(GameManager.Instance.SelectedTeam);
            playerMech.SetArchetype(GameManager.Instance.SelectedMech);
        }
    }
}
