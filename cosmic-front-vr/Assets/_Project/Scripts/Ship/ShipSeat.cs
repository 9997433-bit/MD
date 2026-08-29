using System;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Ship
{
    /// <summary>
    /// Interactive seat on a warship. Player enters via proximity + key / VR grip.
    /// </summary>
    public class ShipSeat : MonoBehaviour
    {
        [SerializeField] private ShipSeatRole role = ShipSeatRole.Pilot;
        [SerializeField] private Transform seatAnchor;
        [SerializeField] private float interactRadius = 3f;
        [SerializeField] private string displayName = "Seat";

        public ShipSeatRole Role => role;
        public Transform SeatAnchor => seatAnchor != null ? seatAnchor : transform;
        public string DisplayName => displayName;
        public bool IsOccupied => Occupant != null;
        public GameObject Occupant { get; private set; }
        public ShipController Ship { get; private set; }

        public event Action<ShipSeat, GameObject> OccupantChanged;

        public void BindShip(ShipController ship)
        {
            Ship = ship;
        }

        public bool TryEnter(GameObject occupant)
        {
            if (IsOccupied || occupant == null)
            {
                return false;
            }

            Occupant = occupant;
            OccupantChanged?.Invoke(this, occupant);
            return true;
        }

        public void Exit()
        {
            if (Occupant == null)
            {
                return;
            }

            Occupant = null;
            OccupantChanged?.Invoke(this, null);
        }

        public bool IsInRange(Vector3 worldPosition)
        {
            return Vector3.Distance(worldPosition, transform.position) <= interactRadius;
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(transform.position, interactRadius);
        }
    }
}
