using FishNet.Connection;
using FishNet.Managing;
using FishNet.Object;
using FishNet.Transporting;
using UnityEngine;
using CosmicFront.AI;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.Network
{
    /// <summary>
    /// Server-side player spawning and team assignment for LAN multiplayer.
    /// </summary>
    public class NetworkMatchManager : NetworkBehaviour
    {
        [SerializeField] private NetworkObject playerPrefab;
        [SerializeField] private Transform[] spawnPoints;
        [SerializeField] private bool spawnAiInMultiplayer = true;
        [SerializeField] private GameObject singlePlayerMechToDisable;

        private int _spawnIndex;
        private int _teamCounter;

        public override void OnStartServer()
        {
            if (singlePlayerMechToDisable != null)
            {
                singlePlayerMechToDisable.SetActive(false);
            }

            NetworkManager.ServerManager.OnRemoteConnectionState += OnRemoteConnectionState;

            foreach (var kvp in NetworkManager.ServerManager.Clients)
            {
                TrySpawnPlayer(kvp.Value);
            }
        }

        public override void OnStopServer()
        {
            NetworkManager.ServerManager.OnRemoteConnectionState -= OnRemoteConnectionState;
        }

        private void OnRemoteConnectionState(NetworkConnection conn, RemoteConnectionStateArgs args)
        {
            if (args.ConnectionState == RemoteConnectionState.Started)
            {
                TrySpawnPlayer(conn);
            }
        }

        private void TrySpawnPlayer(NetworkConnection conn)
        {
            if (playerPrefab == null || conn == null || !conn.IsActive)
            {
                return;
            }

            if (conn.FirstObject != null)
            {
                return;
            }

            var spawn = GetSpawnPoint();
            var team = AssignTeam();

            var instance = Instantiate(playerPrefab, spawn.position, spawn.rotation);
            var controller = instance.GetComponent<MechController>();
            if (controller != null)
            {
                controller.SetTeam(team);
            }

            NetworkManager.ServerManager.Spawn(instance, conn);
        }

        private TeamId AssignTeam()
        {
            _teamCounter++;
            return _teamCounter % 2 == 0 ? TeamId.Orbital : TeamId.Terran;
        }

        private Transform GetSpawnPoint()
        {
            if (spawnPoints == null || spawnPoints.Length == 0)
            {
                return transform;
            }

            var point = spawnPoints[_spawnIndex % spawnPoints.Length];
            _spawnIndex++;
            return point;
        }

        private void Start()
        {
            if (!GameManager.Instance || !GameManager.Instance.IsMultiplayer)
            {
                return;
            }

            if (spawnAiInMultiplayer)
            {
                return;
            }

            var spawner = FindObjectOfType<EnemySpawner>();
            if (spawner != null)
            {
                spawner.enabled = false;
            }
        }
    }
}
