using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// VR controller shortcuts with skill-ring-first ray priority.
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

            var ray = VRRaycastUtility.CenterEyeRay();
            if (_skillRing != null && _skillRing.IsVisible)
                _skillRing.UpdateVrHover(ray);

            if (Input.GetButtonDown("XRI_Right_TriggerButton") || Input.GetKeyDown(KeyCode.JoystickButton2))
                HandleTrigger(ray);

            if (Input.GetButtonDown("XRI_Right_GripButton") || Input.GetKeyDown(KeyCode.JoystickButton4))
                HandleGrip(ray);

            if (Input.GetButtonDown("XRI_Right_PrimaryButton") || Input.GetKeyDown(KeyCode.JoystickButton0))
                _director.EndCurrentPhase();

            if (Input.GetButtonDown("XRI_Right_SecondaryButton") || Input.GetKeyDown(KeyCode.JoystickButton1))
                _director.StepAuto();
        }

        private void HandleTrigger(Ray ray)
        {
            if (_skillRing != null && _skillRing.IsVisible)
            {
                if (_skillRing.TryActivateFromRay(ray)) return;
            }

            if (_skillRing != null && _skillRing.AwaitingTarget &&
                VRRaycastUtility.TryHitBoard(ray, out _, out var cell, out _) && cell != null)
            {
                if (_skillRing.TryTargetCell(new GridPos(cell.X, cell.Y)))
                {
                    _desktop.CancelSelection();
                    return;
                }
            }

            if (!VRRaycastUtility.TryHitBoard(ray, out var piece, out var boardCell, out var hit)) return;

            if (piece != null)
            {
                if (_coop != null && !_coop.CanControlUnit(piece.UnitId)) return;
                _desktop.SelectPiece(piece);
                if (_director.State.Phase == BattlePhase.Move)
                    piece.BeginDrag(hit.point);
                else if (_director.State.Phase is BattlePhase.Action or BattlePhase.Weave)
                    ShowSkillRingForPiece(piece);
                return;
            }

            if (boardCell != null && _skillRing != null && _skillRing.AwaitingTarget)
            {
                if (_skillRing.TryTargetCell(new GridPos(boardCell.X, boardCell.Y)))
                    _desktop.CancelSelection();
            }
        }

        private void HandleGrip(Ray ray)
        {
            if (_director.State is BattlePhase.Action or BattlePhase.Weave)
            {
                if (VRRaycastUtility.TryHitBoard(ray, out var piece, out _, out _) && piece != null)
                {
                    if (_coop != null && !_coop.CanControlUnit(piece.UnitId)) return;
                    _desktop.SelectPiece(piece);
                    ShowSkillRingForPiece(piece);
                    return;
                }
            }

            TryShowSkillRingForNearestPiece();
        }

        private void ShowSkillRingForPiece(PieceToken piece)
        {
            var unit = _director.State.Party.Find(u => u.Id == piece.UnitId);
            if (unit != null)
                _skillRing.ShowForUnit(unit.Id, unit.Job, piece.transform.position);
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
            ShowSkillRingForPiece(nearest);
        }
    }
}
