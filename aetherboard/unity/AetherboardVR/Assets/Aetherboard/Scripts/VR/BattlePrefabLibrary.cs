using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Loads battle table prefabs from Resources (installed via Editor menu).
    /// </summary>
    public static class BattlePrefabLibrary
    {
        public const string GridCellPath = "Aetherboard/GridCell";
        public const string PieceTokenPath = "Aetherboard/PieceToken";
        public const string TableBasePath = "Aetherboard/TableBase";
        public const string PreviewRingPath = "Aetherboard/PreviewRing";

        private static GridCell _gridCell;
        private static PieceToken _pieceToken;
        private static GameObject _tableBase;
        private static GameObject _previewRing;
        private static bool _probed;

        public static bool HasPrefabs
        {
            get
            {
                Probe();
                return _gridCell != null && _pieceToken != null;
            }
        }

        public static GridCell GridCellPrefab
        {
            get
            {
                Probe();
                return _gridCell;
            }
        }

        public static PieceToken PieceTokenPrefab
        {
            get
            {
                Probe();
                return _pieceToken;
            }
        }

        public static GameObject TableBasePrefab
        {
            get
            {
                Probe();
                return _tableBase;
            }
        }

        public static GameObject PreviewRingPrefab
        {
            get
            {
                Probe();
                return _previewRing;
            }
        }

        private static void Probe()
        {
            if (_probed) return;
            _probed = true;
            _gridCell = Resources.Load<GridCell>(GridCellPath);
            _pieceToken = Resources.Load<PieceToken>(PieceTokenPath);
            _tableBase = Resources.Load<GameObject>(TableBasePath);
            _previewRing = Resources.Load<GameObject>(PreviewRingPath);
        }
    }
}
