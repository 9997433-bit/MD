using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Optional external art models under Resources/Aetherboard/Art/Models/.
    /// </summary>
    public static class BattleArtCatalog
    {
        private const string ModelRoot = "Aetherboard/Art/Models/";

        public static GameObject LoadPieceModel(JobType job)
        {
            var name = job switch
            {
                JobType.Knight => "Piece_Knight",
                JobType.WhiteMage => "Piece_WhiteMage",
                JobType.BlackMage => "Piece_BlackMage",
                JobType.Bard => "Piece_Bard",
                _ => null
            };
            return string.IsNullOrEmpty(name) ? null : Resources.Load<GameObject>(ModelRoot + name);
        }

        public static GameObject LoadTableBase() =>
            Resources.Load<GameObject>(ModelRoot + "Table_Base");

        public static GameObject LoadGridCell() =>
            Resources.Load<GameObject>(ModelRoot + "Grid_Cell");

        public static GameObject LoadBossHologram(string bossId)
        {
            if (string.IsNullOrEmpty(bossId)) bossId = "earth";
            return Resources.Load<GameObject>($"{ModelRoot}Boss_{bossId}");
        }

        public static bool HasExternalArt =>
            LoadPieceModel(JobType.Knight) != null || LoadTableBase() != null;
    }
}
