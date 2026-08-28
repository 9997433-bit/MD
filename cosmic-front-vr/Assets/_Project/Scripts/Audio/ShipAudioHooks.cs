using UnityEngine;
using CosmicFront.Ship;

namespace CosmicFront.Audio
{
    /// <summary>
    /// Ship audio placeholders: board / thrust loop / turret fire. Attach near ShipCrewMember.
    /// </summary>
    public class ShipAudioHooks : MonoBehaviour
    {
        [SerializeField] private AudioSource reservedSource;
        [SerializeField] private float thrustThreshold = 0.05f;
        [SerializeField] private float turretFireAudioInterval = 0.25f;

        private ShipCrewMember _crew;
        private IShipSeatInputProvider _shipInput;
        private bool _wasBoarded;
        private bool _thrustPlaying;
        private float _turretAudioCooldown;

        private void Awake()
        {
            _crew = GetComponent<ShipCrewMember>();
            _shipInput = GetComponent<IShipSeatInputProvider>();
            GameAudioBus.EnsureExists();
        }

        private void OnDisable()
        {
            if (_thrustPlaying)
            {
                GameAudioBus.Instance?.StopLoop("ship_thrust");
                _thrustPlaying = false;
            }
        }

        private void Update()
        {
            var bus = GameAudioBus.Instance;
            if (bus == null || _crew == null)
            {
                return;
            }

            var boarded = _crew.IsBoarded;
            if (boarded && !_wasBoarded)
            {
                bus.PlayOneShot("ship_board");
            }

            if (!boarded && _wasBoarded && _thrustPlaying)
            {
                bus.StopLoop("ship_thrust");
                _thrustPlaying = false;
            }

            _wasBoarded = boarded;

            if (!boarded)
            {
                return;
            }

            if (_shipInput == null)
            {
                _shipInput = GetComponent<IShipSeatInputProvider>();
                if (_shipInput == null)
                {
                    return;
                }
            }

            var input = _shipInput.ReadShipInput();
            var thrusting = input.Thrust.sqrMagnitude > thrustThreshold * thrustThreshold || input.Boost;
            if (thrusting && !_thrustPlaying)
            {
                bus.PlayLoop("ship_thrust");
                _thrustPlaying = true;
            }
            else if (!thrusting && _thrustPlaying)
            {
                bus.StopLoop("ship_thrust");
                _thrustPlaying = false;
            }

            if (_turretAudioCooldown > 0f)
            {
                _turretAudioCooldown -= Time.deltaTime;
            }

            if (input.FireTurret &&
                _crew.CurrentRole == ShipSeatRole.Gunner &&
                _turretAudioCooldown <= 0f)
            {
                bus.PlayOneShot("ship_turret_fire");
                _turretAudioCooldown = turretFireAudioInterval;
            }
        }
    }
}
