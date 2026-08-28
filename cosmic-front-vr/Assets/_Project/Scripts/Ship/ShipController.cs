using System.Collections.Generic;
using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Ship
{
    /// <summary>
    /// Root warship object. Holds seats, movement, captain console and launch bay.
    /// </summary>
    [RequireComponent(typeof(ShipMovement))]
    [RequireComponent(typeof(HealthSystem))]
    public class ShipController : MonoBehaviour
    {
        [SerializeField] private ShipClass shipClass = ShipClass.Frigate;
        [SerializeField] private TeamId team = TeamId.Terran;
        [SerializeField] private string shipDisplayName = "护卫舰 Aegis";
        [SerializeField] private Transform bridgeCameraAnchor;

        private ShipMovement _movement;
        private HealthSystem _health;
        private ShipCaptainConsole _captain;
        private ShipLaunchBay _launchBay;
        private readonly List<ShipSeat> _seats = new List<ShipSeat>();
        private readonly List<ShipGunnerTurret> _turrets = new List<ShipGunnerTurret>();

        public TeamId Team => team;
        public ShipClass Class => shipClass;
        public string DisplayName => shipDisplayName;
        public HealthSystem Health => _health;
        public ShipMovement Movement => _movement;
        public ShipCaptainConsole Captain => _captain;
        public ShipLaunchBay LaunchBay => _launchBay;
        public Transform BridgeCameraAnchor => bridgeCameraAnchor != null ? bridgeCameraAnchor : transform;
        public IReadOnlyList<ShipSeat> Seats => _seats;

        private void Awake()
        {
            _movement = GetComponent<ShipMovement>();
            _health = GetComponent<HealthSystem>();
            _captain = GetComponentInChildren<ShipCaptainConsole>();
            _launchBay = GetComponentInChildren<ShipLaunchBay>();

            GetComponentsInChildren(true, _seats);
            GetComponentsInChildren(true, _turrets);

            foreach (var seat in _seats)
            {
                seat.BindShip(this);
            }

            if (_captain != null)
            {
                _captain.Bind(_health);
            }

            if (_launchBay != null)
            {
                _launchBay.Bind(this);
            }

            ApplyTeam(team);
            _health.Died += OnShipDestroyed;
        }

        private void OnDestroy()
        {
            if (_health != null)
            {
                _health.Died -= OnShipDestroyed;
            }
        }

        public void ApplyTeam(TeamId newTeam)
        {
            team = newTeam;
            var hp = shipClass == ShipClass.Cruiser ? 800f : 500f;
            var shield = shipClass == ShipClass.Cruiser ? 300f : 200f;
            _health.Configure(team, hp, shield);

            foreach (var turret in _turrets)
            {
                turret.SetTeam(team);
            }
        }

        public ShipSeat FindSeat(ShipSeatRole role)
        {
            foreach (var seat in _seats)
            {
                if (seat.Role == role)
                {
                    return seat;
                }
            }

            return null;
        }

        public ShipSeat FindNearestAvailableSeat(Vector3 worldPos)
        {
            ShipSeat best = null;
            var bestDist = float.MaxValue;
            foreach (var seat in _seats)
            {
                if (seat.IsOccupied || !seat.IsInRange(worldPos))
                {
                    continue;
                }

                var d = Vector3.Distance(worldPos, seat.transform.position);
                if (d < bestDist)
                {
                    bestDist = d;
                    best = seat;
                }
            }

            return best;
        }

        public ShipGunnerTurret GetTurretForSeat(ShipSeat seat)
        {
            if (seat == null || _turrets.Count == 0)
            {
                return null;
            }

            if (seat.Role != ShipSeatRole.Gunner)
            {
                return null;
            }

            return _turrets[0];
        }

        public void ApplyPilotInput(ShipInputState input)
        {
            if (_health == null || !_health.IsAlive)
            {
                return;
            }

            _movement.ApplyInput(input);
        }

        private void OnShipDestroyed(HealthSystem _, GameObject killer)
        {
            foreach (var seat in _seats)
            {
                seat.Exit();
            }

            gameObject.SetActive(false);
        }
    }
}
