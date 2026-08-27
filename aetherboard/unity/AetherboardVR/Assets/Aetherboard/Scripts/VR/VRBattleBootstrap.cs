using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Legacy bootstrap — use RuntimeSceneBootstrap for full auto setup.
    /// </summary>
    public class VRBattleBootstrap : MonoBehaviour
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private BattleTableView table;
        [SerializeField] private bool seatedMode = true;

        private void Start()
        {
            if (director == null) director = GetComponent<BattleDirector>();
            if (table == null) table = GetComponent<BattleTableView>();

            if (table != null && director != null)
            {
                foreach (var piece in FindObjectsOfType<PieceToken>())
                    piece.Inject(director, table);
            }

            if (seatedMode && table != null)
            {
                var pos = table.transform.position;
                table.transform.position = new Vector3(pos.x, 0.75f, pos.z);
            }
        }
    }
}
