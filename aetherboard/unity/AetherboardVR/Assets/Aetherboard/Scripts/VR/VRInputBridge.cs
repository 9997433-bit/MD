using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// VR controller shortcuts: Grip = skill ring, Trigger = confirm, Primary = end phase.
    /// Uses legacy Input when XR Input System bindings are not configured.
    /// </summary>
    public class VRInputBridge : MonoBehaviour
    {
        private BattleDirector _director;
        private BattleTableView _table;
        private SkillRingController _skillRing;
        private DesktopBattleInput _desktop;
        private PieceToken _lastSelected;

        public void Bind(
            BattleDirector director,
            BattleTableView table,
            SkillRingController skillRing,
            DesktopBattleInput desktop)
        {
            _director = director;
            _table = table;
            _skillRing = skillRing;
            _desktop = desktop;
        }

        private void Update()
        {
            if (!XRRigFactory.XrActive || _director == null) return;

            // Common XR bindings (Oculus / OpenXR via legacy axis names when mapped)
            if (Input.GetButtonDown("XRI_Right_GripButton") || Input.GetKeyDown(KeyCode.JoystickButton4))
                TryShowSkillRingForNearestPiece();

            if (Input.GetButtonDown("XRI_Right_PrimaryButton") || Input.GetKeyDown(KeyCode.JoystickButton0))
                _director.EndCurrentPhase();

            if (Input.GetButtonDown("XRI_Right_SecondaryButton") || Input.GetKeyDown(KeyCode.JoystickButton1))
                _director.StepAuto();
        }

        private void TryShowSkillRingForNearestPiece()
        {
            var cam = Camera.main;
            if (cam == null) return;

            PieceToken nearest = null;
            var best = float.MaxValue;
            foreach (var piece in FindObjectsOfType<PieceToken>())
            {
                if (!piece.gameObject.activeInHierarchy) continue;
                var d = Vector3.Distance(cam.transform.position, piece.transform.position);
                if (d < best)
                {
                    best = d;
                    nearest = piece;
                }
            }
            if (nearest == null) return;
            _desktop.SelectPiece(nearest);
            var unit = _director.State.Party.Find(u => u.Id == nearest.UnitId);
            if (unit != null)
                _skillRing.ShowForUnit(unit.Id, unit.Job, nearest.transform.position);
        }
    }
}
