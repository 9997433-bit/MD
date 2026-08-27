using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class BattleTableView : MonoBehaviour
    {
        [SerializeField] private float cellSize = 0.12f;
        [SerializeField] private float tableHeight = 0.02f;
        [SerializeField] private GridCell cellPrefab;
        [SerializeField] private PieceToken piecePrefab;
        [SerializeField] private Transform cellsRoot;
        [SerializeField] private Transform piecesRoot;

        private readonly Dictionary<(int, int), GridCell> _cells = new();
        private readonly Dictionary<string, PieceToken> _pieces = new();
        private bool _built;
        private CoopController _coop;

        public float CellSize => cellSize;

        public void SetCoop(CoopController coop) => _coop = coop;

        /// <summary>
        /// Prefab-first build used by BattleSceneBuilder; falls back to procedural primitives.
        /// </summary>
        public void Build(
            Transform parent,
            BattleDirector director,
            GridSnapHighlighter highlighter = null,
            CoopController coop = null)
        {
            if (_built) return;
            _coop = coop ?? _coop;

            if (BattlePrefabLibrary.HasPrefabs)
                BuildFromLibrary(parent, director, highlighter, coop);
            else
                BuildProcedural(parent, director, highlighter, coop);
        }

        private void Awake()
        {
            if (cellPrefab != null && piecePrefab != null && !_built)
                BuildFromPrefabs();
        }

        public void BuildProcedural(
            Transform parent,
            BattleDirector director,
            GridSnapHighlighter highlighter = null,
            CoopController coop = null)
        {
            if (_built) return;
            _built = true;
            _coop = coop ?? _coop;

            var tableRoot = new GameObject("Table").transform;
            tableRoot.SetParent(parent, false);

            cellsRoot = new GameObject("Cells").transform;
            cellsRoot.SetParent(tableRoot, false);
            piecesRoot = new GameObject("Pieces").transform;
            piecesRoot.SetParent(tableRoot, false);

            ProceduralAssets.CreateTableBase(tableRoot, cellSize * 7.5f);

            for (var y = 0; y < BoardMath.DefaultSize; y++)
            for (var x = 0; x < BoardMath.DefaultSize; x++)
            {
                var go = ProceduralAssets.CreateCell(cellsRoot, cellSize, tableHeight);
                go.transform.localPosition = GridToLocal(x, y);
                var cell = go.AddComponent<GridCell>();
                cell.InitProcedural(x, y, go.GetComponent<Renderer>());
                _cells[(x, y)] = cell;

                if (x == BoardMath.BossPos(BoardMath.DefaultSize).X &&
                    y == BoardMath.BossPos(BoardMath.DefaultSize).Y)
                {
                    var boss = ProceduralAssets.CreateBossMarker(go.transform, cellSize);
                    boss.transform.localPosition = new Vector3(0, 0.08f, 0);
                }
            }

            foreach (var id in new[] { "knight", "white_mage", "black_mage", "bard" })
            {
                var go = ProceduralAssets.CreatePiece(piecesRoot, cellSize);
                go.name = $"Piece_{id}";
                var token = go.AddComponent<PieceToken>();
                token.InitProcedural(go.GetComponent<Renderer>());
                token.UnitId = id;
                token.Inject(director, this, highlighter, _coop);
                _pieces[id] = token;
            }
        }

        private void BuildFromLibrary(
            Transform parent,
            BattleDirector director,
            GridSnapHighlighter highlighter,
            CoopController coop)
        {
            if (_built) return;
            _built = true;

            var tableRoot = new GameObject("Table").transform;
            tableRoot.SetParent(parent, false);

            cellsRoot = new GameObject("Cells").transform;
            cellsRoot.SetParent(tableRoot, false);
            piecesRoot = new GameObject("Pieces").transform;
            piecesRoot.SetParent(tableRoot, false);

            if (BattlePrefabLibrary.TableBasePrefab != null)
                Instantiate(BattlePrefabLibrary.TableBasePrefab, tableRoot);
            else
                ProceduralAssets.CreateTableBase(tableRoot, cellSize * 7.5f);

            var cellPrefab = BattlePrefabLibrary.GridCellPrefab;
            var piecePrefab = BattlePrefabLibrary.PieceTokenPrefab;

            for (var y = 0; y < BoardMath.DefaultSize; y++)
            for (var x = 0; x < BoardMath.DefaultSize; x++)
            {
                var cell = Instantiate(cellPrefab, cellsRoot);
                cell.name = $"Cell_{x}_{y}";
                cell.transform.localPosition = GridToLocal(x, y);
                cell.Init(x, y);
                _cells[(x, y)] = cell;

                if (x == BoardMath.BossPos(BoardMath.DefaultSize).X &&
                    y == BoardMath.BossPos(BoardMath.DefaultSize).Y)
                {
                    var boss = ProceduralAssets.CreateBossMarker(cell.transform, cellSize);
                    boss.transform.localPosition = new Vector3(0, 0.08f, 0);
                }
            }

            foreach (var id in new[] { "knight", "white_mage", "black_mage", "bard" })
            {
                var token = Instantiate(piecePrefab, piecesRoot);
                token.name = $"Piece_{id}";
                token.UnitId = id;
                token.Inject(director, this, highlighter, coop);
                _pieces[id] = token;
            }

            Debug.Log("[Aetherboard] Battle table built from Resources prefabs.");
        }

        private void BuildFromPrefabs()
        {
            if (_built) return;
            _built = true;
            if (cellsRoot == null) cellsRoot = transform;
            if (piecesRoot == null) piecesRoot = transform;

            for (var y = 0; y < BoardMath.DefaultSize; y++)
            for (var x = 0; x < BoardMath.DefaultSize; x++)
            {
                var cell = Instantiate(cellPrefab, cellsRoot);
                cell.name = $"Cell_{x}_{y}";
                cell.transform.localPosition = GridToLocal(x, y);
                cell.Init(x, y);
                _cells[(x, y)] = cell;
            }

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

        public Vector3 GridToLocal(int x, int y)
        {
            var offset = (BoardMath.DefaultSize - 1) * cellSize * 0.5f;
            return new Vector3(x * cellSize - offset, tableHeight, y * cellSize - offset);
        }

        public GridPos WorldToGrid(Vector3 worldPos)
        {
            var local = transform.InverseTransformPoint(worldPos);
            var offset = (BoardMath.DefaultSize - 1) * cellSize * 0.5f;
            var x = Mathf.RoundToInt((local.x + offset) / cellSize);
            var y = Mathf.RoundToInt((local.z + offset) / cellSize);
            return new GridPos(
                Mathf.Clamp(x, 0, BoardMath.DefaultSize - 1),
                Mathf.Clamp(y, 0, BoardMath.DefaultSize - 1));
        }

        public void Bind(BattleState state)
        {
            if (!_built) return;
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
                if (!token.IsBeingManipulated)
                {
                    var world = GridToWorld(unit.Pos.X, unit.Pos.Y);
                    token.transform.position = world + Vector3.up * (cellSize * 0.28f);
                }
                token.SetJob(unit.Job);
                token.RememberHome(unit.Pos);
                token.SetCoopPlayer(GetCoopPlayer(unit.Id));
            }
        }

        private int GetCoopPlayer(string unitId)
        {
            if (_coop == null || _coop.Mode != CoopMode.SplitCoop) return 0;
            return unitId is "knight" or "bard" ? 1 : 2;
        }

        private static bool IsPreview(BattleState state, int x, int y) =>
            state.PreviewCells.Exists(p => p.X == x && p.Y == y);

        public GridCell GetCell(int x, int y) =>
            _cells.TryGetValue((x, y), out var c) ? c : null;

        public PieceToken GetPiece(string unitId) =>
            _pieces.TryGetValue(unitId, out var p) ? p : null;
    }
}
