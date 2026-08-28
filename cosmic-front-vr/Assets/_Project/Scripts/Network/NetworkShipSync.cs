using FishNet.Object;
using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Ship;

namespace CosmicFront.Network
{
    /// <summary>
    /// Network wrapper for warships. Server owns HP; seat boarding via ServerRpc.
    /// </summary>
    [RequireComponent(typeof(ShipController))]
    public class NetworkShipSync : NetworkBehaviour
    {
        private ShipController _ship;
        private NetworkHealthSync _healthSync;

        private void Awake()
        {
            _ship = GetComponent<ShipController>();
            _healthSync = GetComponent<NetworkHealthSync>();
        }

        public override void OnStartServer()
        {
            if (_healthSync != null)
            {
                _healthSync.SetSpawnPoint(transform.position, transform.rotation);
            }
        }

        public void RequestBoard(ShipSeatRole preferredRole)
        {
            if (IsServerInitialized)
            {
                TryBoardLocal(preferredRole);
                return;
            }

            BoardServerRpc(preferredRole);
        }

        [ServerRpc(RequireOwnership = false)]
        private void BoardServerRpc(ShipSeatRole preferredRole, FishNet.Connection.NetworkConnection caller = null)
        {
            // Seat occupancy is resolved on server; clients receive visual parenting via NetworkTransform of crew.
            ObserversBoardAckRpc(preferredRole, caller != null ? caller.ClientId : -1);
        }

        [ObserversRpc]
        private void ObserversBoardAckRpc(ShipSeatRole preferredRole, int clientId)
        {
            if (IsOwner || clientId < 0)
            {
                TryBoardLocal(preferredRole);
            }
        }

        private void TryBoardLocal(ShipSeatRole preferredRole)
        {
            var crew = FindLocalCrew();
            if (crew != null)
            {
                crew.TryBoard(_ship, preferredRole);
            }
        }

        private static ShipCrewMember FindLocalCrew()
        {
            var crews = FindObjectsOfType<ShipCrewMember>();
            foreach (var crew in crews)
            {
                if (crew.CompareTag("Player") || crew.isActiveAndEnabled)
                {
                    return crew;
                }
            }

            return null;
        }

        public void ConfigureTeam(TeamId team)
        {
            _ship?.ApplyTeam(team);
        }
    }
}
