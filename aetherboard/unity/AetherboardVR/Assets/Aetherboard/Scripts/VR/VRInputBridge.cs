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
        private SkillRingController _skillRing;
        private DesktopBattleInput _desktop;
        private CoopController _coop;

        public void Bind(
            BattleDirector director,
            BattleTableView table,
            SkillRingController skillRing,
            DesktopBattleInput desktop,
            CoopController coop = null)
        {
            _director = director;
            _skillRing = skillRing;
            _desktop = desktop;
            _coop = coop;
        }

        private void Update()
        {
            if (!XRRigFactory.XrActive || _director == null) return;

            if (Input.GetButtonDown("XRI_Right_TriggerButton") || Input.GetKeyDown(KeyCode.JoystickButton2))
                TrySelectUnderGaze();

            if (Input.GetButtonDown("XRI_Right_GripButton") || Input.GetKeyDown(KeyCode.JoystickButton4))
                TryShowSkillRingForNearestPiece();

            if (Input.GetButtonDown("XRI_Right_PrimaryButton") || Input.GetKeyDown(KeyCode.JoystickButton0))
                _director.EndCurrentPhase();

            if (Input.GetButtonDown("XRI_Right_SecondaryButton") || Input.GetKeyDown(KeyCode.JoystickButton1))
                _director.StepAuto();
        }

        private void TrySelectUnderGaze()
        {
            var cam = Camera.main;
            if (cam == null) return;
            var ray = cam.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f));
            if (!Physics.Raycast(ray, out var hit, 8f)) return;

            var piece = hit.collider.GetComponentInParent<PieceToken>();
            if (piece != null)
            {
                if (_coop != null && !_coop.CanControlUnit(piece.UnitId)) return;
                _desktop.SelectPiece(piece);
                if (_director.State.Phase == BattlePhase.Move)
                    piece.BeginDrag(hit.point);
                else if (_director.State.Phase is BattlePhase.Action or BattlePhase.Weave)
                {
                    var unit = _director.State.Party.Find(u => u.Id == piece.UnitId);
                    if (unit != null)
                        _skillRing.ShowForUnit(unit.Id, unit.Job, piece.transform.position);
                }
                return;
            }

            var cell = hit.collider.GetComponentInParent<GridCell>();
            if (cell == null) return;
            var dest = new GridPos(cell.X, cell.Y);
            if (_skillRing != null && _skillRing.AwaitingTarget)
            {
                if (_skillRing.TryTargetCell(dest))
                    _desktop.CancelSelection();
            }
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
            if (_coop != null && !_coop.CanControlUnit(nearest.UnitId)) return;
            _desktop.SelectPiece(nearest);
            var unit = _director.State.Party.Find(u => u.Id == nearest.UnitId);
            if (unit != null)
                _skillRing.ShowForUnit(unit.Id, unit.Job, nearest.transform.position);
        }
    }
}
