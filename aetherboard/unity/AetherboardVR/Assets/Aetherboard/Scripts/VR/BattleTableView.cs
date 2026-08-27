using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Renders the 7x7 board, cell states, and piece tokens.
    /// </summary>
    public class BattleTableView : MonoBehaviour
    {
        [SerializeField] private float cellSize = 0.12f;
        [SerializeField] private float tableHeight = 0.8f;
        [SerializeField] private GridCell cellPrefab;
        [SerializeField] private PieceToken piecePrefab;
        [SerializeField] private Transform cellsRoot;
        [SerializeField] private Transform piecesRoot;

        private readonly Dictionary<(int, int), GridCell> _cells = new();
        private readonly Dictionary<string, PieceToken> _pieces = new();

        private void Awake()
        {
            if (cellsRoot == null) cellsRoot = transform;
            if (piecesRoot == null) piecesRoot = transform;
            BuildGrid();
            BuildPieces();
        }

        private void BuildGrid()
        {
            for (var y = 0; y < BoardMath.DefaultSize; y++)
            for (var x = 0; x < BoardMath.DefaultSize; x++)
            {
                var cell = Instantiate(cellPrefab, cellsRoot);
                cell.name = $"Cell_{x}_{y}";
                cell.transform.localPosition = GridToLocal(x, y);
                cell.Init(x, y);
                _cells[(x, y)] = cell;
            }
        }

        private void BuildPieces()
        {
            foreach (var job in new[] { "knight", "white_mage", "black_mage", "bard" })
            {
                var token = Instantiate(piecePrefab, piecesRoot);
                token.name = $"Piece_{job}";
                token.UnitId = job;
                _pieces[job] = token;
            }
        }

        public Vector3 GridToWorld(int x, int y) =>
            transform.TransformPoint(GridToLocal(x, y));

        private Vector3 GridToLocal(int x, int y)
        {
            var offset = (BoardMath.DefaultSize - 1) * cellSize * 0.5f;
            return new Vector3(x * cellSize - offset, tableHeight, y * cellSize - offset);
        }

        public void Bind(BattleState state)
        {
            for (var y = 0; y < state.BoardSize; y++)
            for (var x = 0; x < state.BoardSize; x++)
            {
                if (_cells.TryGetValue((x, y), out var cell))
                    cell.SetKind(state.Cells[y, x], IsPreview(state, x, y));
            }

            foreach (var unit in state.Party)
            {
                if (!_pieces.TryGetValue(unit.Id, out var token)) continue;
                token.gameObject.SetActive(unit.Alive);
                if (!unit.Alive) continue;
                token.transform.position = GridToWorld(unit.Pos.X, unit.Pos.Y);
                token.SetJob(unit.Job);
            }
        }

        private static bool IsPreview(BattleState state, int x, int y) =>
            state.PreviewCells.Exists(p => p.X == x && p.Y == y);

        public GridCell GetCell(int x, int y) =>
            _cells.TryGetValue((x, y), out var c) ? c : null;
    }
}
