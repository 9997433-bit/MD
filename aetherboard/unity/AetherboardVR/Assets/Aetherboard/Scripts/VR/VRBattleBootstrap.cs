using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Scene bootstrap: wires references and configures seated table height.
    /// </summary>
    public class VRBattleBootstrap : MonoBehaviour
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private BattleTableView table;
        [SerializeField] private SkillRingController skillRing;
        [SerializeField] private bool seatedMode = true;
        [SerializeField] private float seatedTableYOffset = 0.75f;

        private void Start()
        {
            if (seatedMode && table != null)
            {
                var pos = table.transform.position;
                table.transform.position = new Vector3(pos.x, seatedTableYOffset, pos.z);
            }

            foreach (var piece in FindObjectsOfType<PieceToken>())
            {
                piece.Inject(director, table);
            }

            if (skillRing != null && director != null)
                skillRing.GetComponent<SkillRingController>();
        }
    }
}
