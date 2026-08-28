using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Player;
using CosmicFront.UI;

namespace CosmicFront.Ship
{
    /// <summary>
    /// Local player component that boards ship seats and routes input by role.
    /// Attach to player avatar / mech root when near a ship.
    /// </summary>
    public class ShipCrewMember : MonoBehaviour
    {
        [SerializeField] private float boardKeyHold = 0.2f;
        [SerializeField] private KeyCode boardKey = KeyCode.F;
        [SerializeField] private ShipSeatRole preferredRole = ShipSeatRole.Pilot;

        private ShipSeat _currentSeat;
        private ShipController _currentShip;
        private ShipGunnerTurret _turret;
        private IShipSeatInputProvider _shipInput;
        private MechController _mech;
        private Collider _collider;
        private Rigidbody _rb;
        private bool _boarded;
        private Vector3 _preBoardPosition;

        public bool IsBoarded => _boarded;
        public ShipSeatRole CurrentRole => _currentSeat != null ? _currentSeat.Role : ShipSeatRole.None;
        public ShipController CurrentShip => _currentShip;

        private void Awake()
        {
            _mech = GetComponent<MechController>();
            _collider = GetComponent<Collider>();
            _rb = GetComponent<Rigidbody>();
            _shipInput = GetComponent<IShipSeatInputProvider>() ?? gameObject.AddComponent<ShipSeatInputBridge>();
        }

        private void Update()
        {
            if (_boarded)
            {
                HandleBoardedUpdate();
                return;
            }

            if (Input.GetKeyDown(boardKey) || Input.GetKeyDown(KeyCode.B))
            {
                TryBoardNearby();
            }
        }

        private void FixedUpdate()
        {
            if (!_boarded || _currentShip == null || _shipInput == null)
            {
                return;
            }

            var input = _shipInput.ReadShipInput();
            ProcessRoleInput(input);
        }

        public bool TryBoard(ShipController ship, ShipSeatRole preferred = ShipSeatRole.None)
        {
            if (ship == null || _boarded)
            {
                return false;
            }

            ShipSeat seat = null;
            if (preferred != ShipSeatRole.None)
            {
                seat = ship.FindSeat(preferred);
                if (seat != null && seat.IsOccupied)
                {
                    seat = null;
                }
            }

            seat ??= ship.FindNearestAvailableSeat(transform.position);
            seat ??= ship.FindSeat(ShipSeatRole.Pilot) ?? ship.FindSeat(ShipSeatRole.Gunner) ??
                     ship.FindSeat(ShipSeatRole.Captain) ?? ship.FindSeat(ShipSeatRole.LaunchBay);

            if (seat == null || seat.IsOccupied)
            {
                return false;
            }

            return EnterSeat(ship, seat);
        }

        public void ExitShip()
        {
            if (!_boarded)
            {
                return;
            }

            _currentSeat?.Exit();
            _currentSeat = null;
            _currentShip = null;
            _turret = null;
            _boarded = false;

            if (_collider != null)
            {
                _collider.enabled = true;
            }

            if (_rb != null)
            {
                _rb.isKinematic = false;
            }

            if (_mech != null)
            {
                _mech.enabled = true;
            }

            transform.SetParent(null, true);
            transform.position = _preBoardPosition + Vector3.up * 2f;
        }

        private bool EnterSeat(ShipController ship, ShipSeat seat)
        {
            if (!seat.TryEnter(gameObject))
            {
                return false;
            }

            _preBoardPosition = transform.position;
            _currentShip = ship;
            _currentSeat = seat;
            _turret = ship.GetTurretForSeat(seat);
            _boarded = true;

            if (_collider != null)
            {
                _collider.enabled = false;
            }

            if (_rb != null)
            {
                _rb.isKinematic = true;
                _rb.velocity = Vector3.zero;
            }

            if (_mech != null)
            {
                _mech.enabled = false;
            }

            transform.SetParent(seat.SeatAnchor, false);
            transform.localPosition = Vector3.zero;
            transform.localRotation = Quaternion.identity;

            BindCameraToSeat(seat);
            return true;
        }

        private void TryBoardNearby()
        {
            var ships = FindObjectsOfType<ShipController>();
            ShipController nearest = null;
            var best = float.MaxValue;
            foreach (var ship in ships)
            {
                if (!ship.Health.IsAlive)
                {
                    continue;
                }

                var d = Vector3.Distance(transform.position, ship.transform.position);
                if (d < best && d < 25f)
                {
                    best = d;
                    nearest = ship;
                }
            }

            if (nearest != null)
            {
                TryBoard(nearest, preferredRole);
            }
        }

        private void HandleBoardedUpdate()
        {
            if (_shipInput == null)
            {
                return;
            }

            var input = _shipInput.ReadShipInput();
            if (input.ExitSeat || Input.GetKeyDown(KeyCode.X))
            {
                ExitShip();
            }
        }

        private void ProcessRoleInput(ShipInputState input)
        {
            if (_currentSeat == null || _currentShip == null)
            {
                return;
            }

            switch (_currentSeat.Role)
            {
                case ShipSeatRole.Pilot:
                    _currentShip.ApplyPilotInput(input);
                    break;
                case ShipSeatRole.Gunner:
                    if (_turret != null)
                    {
                        _turret.ApplyAim(input.Yaw, input.Pitch);
                        if (input.FireTurret)
                        {
                            _turret.TryFire(gameObject);
                        }
                    }

                    break;
                case ShipSeatRole.Captain:
                    if (input.UseCaptainAbility)
                    {
                        _currentShip.Captain?.TryActivate();
                    }

                    break;
                case ShipSeatRole.LaunchBay:
                    if (input.RequestLaunch)
                    {
                        TryLaunchFromBay();
                    }

                    break;
            }
        }

        private void TryLaunchFromBay()
        {
            if (_currentShip?.LaunchBay == null)
            {
                return;
            }

            var team = GameManager.Instance != null ? GameManager.Instance.SelectedTeam : _currentShip.Team;
            var archetype = GameManager.Instance != null
                ? GameManager.Instance.SelectedMech
                : MechArchetype.Light;

            var launched = _currentShip.LaunchBay.TryLaunch(team, archetype, gameObject);
            if (launched == null)
            {
                return;
            }

            ExitShip();

            // Local presentation: transfer control to launched mech if we are the local player.
            if (CompareTag("Player"))
            {
                var binder = FindObjectOfType<PlayerMechBinder>();
                var cockpit = launched.transform.Find("YawPivot/PitchPivot/CockpitAnchor");
                if (binder != null && cockpit != null)
                {
                    binder.Bind(launched.GetComponent<MechController>(), cockpit);
                }

                var hud = FindObjectOfType<CockpitHUD>();
                hud?.Bind(launched.GetComponent<MechController>());

                launched.tag = "Player";
                gameObject.SetActive(false);
            }
        }

        private void BindCameraToSeat(ShipSeat seat)
        {
            var cam = Camera.main;
            if (cam == null)
            {
                return;
            }

            var anchor = seat.SeatAnchor;
            if (seat.Role == ShipSeatRole.Captain && _currentShip.BridgeCameraAnchor != null)
            {
                anchor = _currentShip.BridgeCameraAnchor;
            }

            cam.transform.SetParent(anchor, false);
            cam.transform.localPosition = Vector3.zero;
            cam.transform.localRotation = Quaternion.identity;

            var binder = FindObjectOfType<PlayerMechBinder>();
            if (binder != null)
            {
                binder.Bind(null, anchor);
            }
        }
    }
}
