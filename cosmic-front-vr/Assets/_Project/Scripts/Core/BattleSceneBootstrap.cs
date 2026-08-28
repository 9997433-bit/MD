using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Player;
using CosmicFront.Ship;
using CosmicFront.UI;

namespace CosmicFront.Core
{
    /// <summary>
    /// Place in battle scene: wires player mech, HUD, optional ship boarding.
    /// </summary>
    public class BattleSceneBootstrap : MonoBehaviour
    {
        [SerializeField] private MechController playerMech;
        [SerializeField] private PlayerMechBinder playerBinder;
        [SerializeField] private CockpitHUD cockpitHud;
        [SerializeField] private Camera fallbackCamera;
        [SerializeField] private float shipBoardDelay = 0.35f;

        private void Start()
        {
            if (GameManager.Instance != null)
            {
                if (GameManager.Instance.IsMultiplayer)
                {
                    if (playerMech != null)
                    {
                        playerMech.gameObject.SetActive(false);
                    }

                    GameManager.Instance.OnBattleSceneLoaded();
                    return;
                }

                ApplyLoadoutFromGameManager();
                GameManager.Instance.OnBattleSceneLoaded();
            }

            if (playerMech != null)
            {
                var cockpit = playerMech.transform.Find("YawPivot/PitchPivot/CockpitAnchor");
                if (cockpit == null)
                {
                    cockpit = playerMech.transform.Find("CockpitAnchor");
                }

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

                if (GameManager.Instance != null &&
                    GameManager.Instance.SelectedSpawn != SpawnPreference.Mech)
                {
                    Invoke(nameof(TryAutoBoardShip), shipBoardDelay);
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

        private void TryAutoBoardShip()
        {
            if (playerMech == null || GameManager.Instance == null)
            {
                return;
            }

            var crew = playerMech.GetComponent<ShipCrewMember>();
            if (crew == null)
            {
                crew = playerMech.gameObject.AddComponent<ShipCrewMember>();
            }

            var preferred = GameManager.Instance.SelectedSpawn switch
            {
                SpawnPreference.ShipPilot => ShipSeatRole.Pilot,
                SpawnPreference.ShipGunner => ShipSeatRole.Gunner,
                SpawnPreference.ShipCaptain => ShipSeatRole.Captain,
                _ => ShipSeatRole.None
            };

            var ships = FindObjectsOfType<ShipController>();
            foreach (var ship in ships)
            {
                if (ship.Team != GameManager.Instance.SelectedTeam)
                {
                    continue;
                }

                if (crew.TryBoard(ship, preferred))
                {
                    return;
                }
            }

            // Fallback: any friendly-available ship
            foreach (var ship in ships)
            {
                if (crew.TryBoard(ship, preferred))
                {
                    return;
                }
            }
        }
    }
}
