using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Ship;
using FishNet.Object;

namespace CosmicFront.Network
{
    /// <summary>
    /// Spawns team warships at match start (server / single-player bootstrap).
    /// </summary>
    public class NetworkShipSpawner : MonoBehaviour
    {
        [SerializeField] private GameObject shipPrefab;
        [SerializeField] private Transform terranSpawn;
        [SerializeField] private Transform orbitalSpawn;
        [SerializeField] private bool spawnOnStart = true;
        [SerializeField] private bool spawnBothTeams = true;

        private void Start()
        {
            if (!spawnOnStart || shipPrefab == null)
            {
                return;
            }

            var nm = FishNet.InstanceFinder.NetworkManager;
            var isMultiplayer = GameManager.Instance != null && GameManager.Instance.IsMultiplayer;
            if (isMultiplayer && nm != null && !nm.IsServerStarted)
            {
                return;
            }

            SpawnTeamShip(TeamId.Terran, terranSpawn);
            if (spawnBothTeams)
            {
                SpawnTeamShip(TeamId.Orbital, orbitalSpawn);
            }
        }

        private void SpawnTeamShip(TeamId team, Transform spawn)
        {
            if (spawn == null)
            {
                return;
            }

            var go = Instantiate(shipPrefab, spawn.position, spawn.rotation);
            var ship = go.GetComponent<ShipController>();
            ship?.ApplyTeam(team);

            var nm = FishNet.InstanceFinder.NetworkManager;
            var nob = go.GetComponent<NetworkObject>();
            if (nm != null && nm.IsServerStarted && nob != null)
            {
                nm.ServerManager.Spawn(nob);
            }

            var net = go.GetComponent<NetworkShipSync>();
            net?.ConfigureTeam(team);
        }
    }
}
