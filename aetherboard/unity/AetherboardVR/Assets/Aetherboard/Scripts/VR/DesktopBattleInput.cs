using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Mouse/keyboard control for Editor and non-VR testing.
    /// Click piece to select, click cell to move or target skill.
    /// </summary>
    public class DesktopBattleInput : MonoBehaviour
    {
        private BattleDirector _director;
        private BattleTableView _table;
        private PieceToken _selected;
        private string _pendingSkillId;
        private Camera _cam;

        public void Bind(BattleDirector director, BattleTableView table)
        {
            _director = director;
            _table = table;
            _cam = Camera.main;
        }

        private void Update()
        {
            if (_director == null) return;

            if (Input.GetKeyDown(KeyCode.E)) _director.EndCurrentPhase();
            if (Input.GetKeyDown(KeyCode.A)) _director.StepAuto();
            if (Input.GetKeyDown(KeyCode.Alpha1)) _director.SetBoss("earth");
            if (Input.GetKeyDown(KeyCode.Alpha2)) _director.SetBoss("wind");

            if (_cam == null) _cam = Camera.main;
            if (_cam == null) return;

            if (Input.GetMouseButtonDown(0))
                HandleClick();
            if (Input.GetMouseButton(0) && _selected != null && _director.State.Phase == BattlePhase.Move)
            {
                if (Raycast(out var hit))
                    _selected.DragTo(hit.point);
            }
            if (Input.GetMouseButtonUp(0) && _selected != null)
            {
                _selected.EndDrag();
                _selected = null;
            }
        }

        private void HandleClick()
        {
            if (!Raycast(out var hit)) return;

            var piece = hit.collider.GetComponentInParent<PieceToken>();
            if (piece != null)
            {
                SelectPiece(piece);
                if (_director.State.Phase == BattlePhase.Move)
                    piece.BeginDrag(hit.point);
                return;
            }

            var cell = hit.collider.GetComponentInParent<GridCell>();
            if (cell == null) return;
            var dest = new GridPos(cell.X, cell.Y);

            if (_selected == null) return;

            if (!string.IsNullOrEmpty(_pendingSkillId))
            {
                _director.TryUseSkill(_selected.UnitId, _pendingSkillId, dest);
                _pendingSkillId = null;
                _selected.SetSelected(false);
                _selected = null;
                return;
            }

            if (_director.State.Phase == BattlePhase.Move)
                _director.TryMove(_selected.UnitId, dest);
        }

        public void SelectPiece(PieceToken piece)
        {
            if (_selected != null) _selected.SetSelected(false);
            _selected = piece;
            _selected.SetSelected(true);
        }

        public void QueueSkill(string skillId) => _pendingSkillId = skillId;

        private bool Raycast(out RaycastHit hit)
        {
            var ray = _cam.ScreenPointToRay(Input.mousePosition);
            return Physics.Raycast(ray, out hit, 50f);
        }
    }
}
