using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class DesktopBattleInput : MonoBehaviour
    {
        private BattleDirector _director;
        private BattleTableView _table;
        private SkillRingController _skillRing;
        private CoopController _coop;
        private PieceToken _selected;
        private Camera _cam;

        public void Bind(
            BattleDirector director,
            BattleTableView table,
            SkillRingController skillRing,
            CoopController coop)
        {
            _director = director;
            _table = table;
            _skillRing = skillRing;
            _coop = coop;
            _cam = Camera.main;
        }

        private void Update()
        {
            if (_director == null) return;

            if (Input.GetKeyDown(KeyCode.E)) _director.EndCurrentPhase();
            if (Input.GetKeyDown(KeyCode.A)) _director.StepAuto();
            if (Input.GetKeyDown(KeyCode.Alpha1)) _director.SetBoss("earth");
            if (Input.GetKeyDown(KeyCode.Alpha2)) _director.SetBoss("wind");
            if (Input.GetKeyDown(KeyCode.Escape)) CancelSelection();
            if (Input.GetKeyDown(KeyCode.C))
            {
                _coop?.ToggleMode();
                _director.RefreshAllViews();
            }
            if (Input.GetKeyDown(KeyCode.Tab)) _coop?.SwitchActivePlayer();
            if (Input.GetKeyDown(KeyCode.F5)) _director.SaveCheckpoint();
            if (Input.GetKeyDown(KeyCode.F9)) _director.RestoreLastSnapshot();

            if (_cam == null) _cam = Camera.main;
            if (_cam == null) return;

            if (Input.GetMouseButtonDown(0)) HandleClick();
            if (Input.GetMouseButton(0) && _selected != null &&
                _director.State.Phase == BattlePhase.Move && !_skillRing.AwaitingTarget)
            {
                if (Raycast(out var hit)) _selected.DragTo(hit.point);
            }
            if (Input.GetMouseButtonUp(0) && _selected != null &&
                _director.State.Phase == BattlePhase.Move && !_skillRing.AwaitingTarget)
            {
                _selected.EndDrag();
            }
            if (Input.GetMouseButtonDown(1)) TryOpenSkillRing();
        }

        private void HandleClick()
        {
            if (!Raycast(out var hit)) return;
            if (_skillRing != null && _skillRing.TrySelectChip(hit)) return;

            var piece = hit.collider.GetComponentInParent<PieceToken>();
            if (piece != null)
            {
                if (_coop != null && !_coop.CanControlUnit(piece.UnitId))
                {
                    Debug.Log($"[Coop] 当前由 {_coop.ActivePlayerLabel} 控制");
                    return;
                }
                SelectPiece(piece);
                if (_director.State.Phase == BattlePhase.Move)
                    piece.BeginDrag(hit.point);
                else if (_director.State.Phase is BattlePhase.Action or BattlePhase.Weave)
                    ShowSkillRing(piece);
                return;
            }

            var cell = hit.collider.GetComponentInParent<GridCell>();
            if (cell == null) return;
            var dest = new GridPos(cell.X, cell.Y);

            if (_skillRing != null && _skillRing.AwaitingTarget)
            {
                if (_skillRing.TryTargetCell(dest)) CancelSelection();
                return;
            }

            if (_selected == null) return;
            if (_director.State.Phase == BattlePhase.Move &&
                _director.TryMove(_selected.UnitId, dest))
            {
                _selected.SnapToGrid(dest);
            }
        }

        private void TryOpenSkillRing()
        {
            if (_selected != null) ShowSkillRing(_selected);
        }

        private void ShowSkillRing(PieceToken piece)
        {
            if (_skillRing == null) return;
            if (_coop != null && !_coop.CanControlUnit(piece.UnitId)) return;
            var unit = _director.State.Party.Find(u => u.Id == piece.UnitId);
            if (unit == null || !unit.Alive) return;
            if (_director.State.Phase is not (BattlePhase.Action or BattlePhase.Weave)) return;
            _skillRing.ShowForUnit(unit.Id, unit.Job, piece.transform.position);
        }

        public void SelectPiece(PieceToken piece)
        {
            if (_selected != null) _selected.SetSelected(false);
            _selected = piece;
            _selected.SetSelected(true);
        }

        public void CancelSelection()
        {
            _skillRing?.Hide();
            if (_selected != null) _selected.SetSelected(false);
            _selected = null;
        }

        private bool Raycast(out RaycastHit hit)
        {
            hit = default;
            if (_cam == null) return false;
            var ray = _cam.ScreenPointToRay(Input.mousePosition);
            return Physics.Raycast(ray, out hit, 100f);
        }
    }
}
