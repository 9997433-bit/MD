using FishNet.Object;
using UnityEngine;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Player;
using CosmicFront.Tuning;
using CosmicFront.UI;

namespace CosmicFront.Network
{
    /// <summary>
    /// Network authority wrapper for player mechs. Owner drives input; server validates weapons.
    /// </summary>
    [RequireComponent(typeof(MechController))]
    public class NetworkMechSync : NetworkBehaviour
    {
        private MechController _mech;
        private MechInputRouter _inputRouter;
        private WeaponPrimary _primary;
        private WeaponSecondary _secondary;
        private LockOnSystem _lockOn;

        public bool IsLocalPlayer => IsOwner;

        private void Awake()
        {
            _mech = GetComponent<MechController>();
            _inputRouter = GetComponent<MechInputRouter>();
            _primary = GetComponent<WeaponPrimary>();
            _secondary = GetComponent<WeaponSecondary>();
            _lockOn = GetComponent<LockOnSystem>();
        }

        public override void OnStartNetwork()
        {
            ApplyControlOwnership();
        }

        public override void OnOwnershipClient(NetworkConnection prevOwner)
        {
            ApplyControlOwnership();
        }

        public override void OnStartClient()
        {
            if (IsOwner && GameManager.Instance != null)
            {
                SubmitLoadoutServerRpc(GameManager.Instance.SelectedTeam, GameManager.Instance.SelectedMech);
            }
        }

        [ServerRpc]
        private void SubmitLoadoutServerRpc(TeamId team, MechArchetype archetype)
        {
            ConfigureOwnerLoadout(team, archetype);
        }

        public void ConfigureOwnerLoadout(TeamId team, MechArchetype archetype)
        {
            if (_mech == null)
            {
                return;
            }

            _mech.SetTeam(team);
            _mech.SetArchetype(archetype);
        }

        public void RequestPrimaryFire(Transform origin, Transform lockTarget)
        {
            if (!IsOwner)
            {
                return;
            }

            if (IsServerInitialized)
            {
                ExecutePrimaryFire(origin, lockTarget);
                return;
            }

            var lockNetId = lockTarget != null ? lockTarget.GetComponentInParent<NetworkObject>() : null;
            FirePrimaryServerRpc(
                origin != null ? origin.position : transform.position,
                origin != null ? origin.forward : transform.forward,
                lockNetId != null ? lockNetId.ObjectId : 0);
        }

        public void RequestSecondaryFire(Transform origin, Transform lockTarget)
        {
            if (!IsOwner)
            {
                return;
            }

            if (IsServerInitialized)
            {
                ExecuteSecondaryFire(origin, lockTarget);
                return;
            }

            var lockNetId = lockTarget != null ? lockTarget.GetComponentInParent<NetworkObject>() : null;
            FireSecondaryServerRpc(
                origin != null ? origin.position : transform.position,
                origin != null ? origin.forward : transform.forward,
                lockNetId != null ? lockNetId.ObjectId : 0);
        }

        [ServerRpc]
        private void FirePrimaryServerRpc(Vector3 origin, Vector3 forward, int lockObjectId)
        {
            var originTransform = _mech.FireOrigin;
            var lockTarget = ResolveLockTarget(lockObjectId);
            ExecutePrimaryFire(originTransform, lockTarget);
        }

        [ServerRpc]
        private void FireSecondaryServerRpc(Vector3 origin, Vector3 forward, int lockObjectId)
        {
            var originTransform = _mech.FireOrigin;
            var lockTarget = ResolveLockTarget(lockObjectId);
            ExecuteSecondaryFire(originTransform, lockTarget);
        }

        private void ExecutePrimaryFire(Transform origin, Transform lockTarget)
        {
            if (_primary == null)
            {
                return;
            }

            _primary.TryFire(origin, lockTarget, gameObject);
        }

        private void ExecuteSecondaryFire(Transform origin, Transform lockTarget)
        {
            if (_secondary == null)
            {
                return;
            }

            _secondary.TryFire(origin, lockTarget, gameObject);
        }

        private Transform ResolveLockTarget(int lockObjectId)
        {
            if (lockObjectId == 0)
            {
                return null;
            }

            if (NetworkManager.ServerManager.Objects.Spawned.TryGetValue(lockObjectId, out var netObj))
            {
                return netObj.transform;
            }

            return null;
        }

        private void ApplyControlOwnership()
        {
            var enableControl = IsOwner;

            if (_inputRouter != null)
            {
                _inputRouter.enabled = enableControl;
            }

            var fallback = GetComponent<FallbackMechInput>();
            if (fallback != null)
            {
                fallback.enabled = enableControl;
            }

            var vr = GetComponent<VRMechInput>();
            if (vr != null)
            {
                vr.enabled = enableControl;
            }

            if (IsOwner)
            {
                SetupLocalPresentation();
            }
        }

        private void SetupLocalPresentation()
        {
            if (GameManager.Instance != null)
            {
                _mech.SetTeam(GameManager.Instance.SelectedTeam);
                _mech.SetArchetype(GameManager.Instance.SelectedMech);
            }

            var cockpit = transform.Find("YawPivot/PitchPivot/CockpitAnchor");
            if (cockpit == null)
            {
                cockpit = transform;
            }

            var xrRig = FindObjectOfType<PlayerMechBinder>();
            if (xrRig != null)
            {
                xrRig.Bind(_mech, cockpit);
            }

            var hud = FindObjectOfType<CockpitHUD>();
            if (hud != null)
            {
                hud.Bind(_mech);
            }

            var cam = Camera.main;
            if (cam != null)
            {
                cam.transform.SetParent(cockpit, false);
                cam.transform.localPosition = Vector3.zero;
                cam.transform.localRotation = Quaternion.identity;
            }
        }
    }
}
