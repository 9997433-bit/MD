using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Highlights the grid cell under a dragged / grabbed piece.
    /// </summary>
    public class GridSnapHighlighter : MonoBehaviour
    {
        [SerializeField] private Color hoverColor = new(0.25f, 0.85f, 1f, 0.9f);
        [SerializeField] private Color invalidColor = new(0.9f, 0.2f, 0.2f, 0.85f);

        private BattleTableView _table;
        private GridPos? _current;
        private GridCell _currentCell;
        private bool _active;

        public void Begin(BattleTableView table, float _)
        {
            _table = table;
            _active = true;
            Clear();
        }

        public void SetHover(GridPos pos)
        {
            if (!_active || _table == null) return;
            if (_current.HasValue && _current.Value.X == pos.X && _current.Value.Y == pos.Y) return;

            Clear();
            _current = pos;
            _currentCell = _table.GetCell(pos.X, pos.Y);
            if (_currentCell != null)
                _currentCell.SetHighlight(hoverColor);
        }

        public void SetInvalid(GridPos pos)
        {
            if (!_active || _table == null) return;
            Clear();
            _current = pos;
            _currentCell = _table.GetCell(pos.X, pos.Y);
            if (_currentCell != null)
                _currentCell.SetHighlight(invalidColor);
        }

        public void End()
        {
            _active = false;
            Clear();
            _table = null;
        }

        private void Clear()
        {
            if (_currentCell != null)
            {
                _currentCell.ClearHighlight();
                _currentCell = null;
            }
            _current = null;
        }
    }
}
