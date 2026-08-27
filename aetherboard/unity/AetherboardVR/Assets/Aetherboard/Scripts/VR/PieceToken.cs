using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Grabbable piece token. On release, snaps to nearest valid grid cell.
    /// </summary>
    [RequireComponent(typeof(XRGrabInteractable))]
    public class PieceToken : MonoBehaviour
    {
        [SerializeField] private Renderer body;
        [SerializeField] private Color knightColor = new(0.2f, 0.5f, 0.8f);
        [SerializeField] private Color healerColor = new(0.2f, 0.7f, 0.35f);
        [SerializeField] private Color mageColor = new(0.55f, 0.25f, 0.75f);
        [SerializeField] private Color bardColor = new(0.85f, 0.45f, 0.1f);

        public string UnitId { get; set; }

        private BattleDirector _director;
        private BattleTableView _table;
        private XRGrabInteractable _grab;
        private GridPos _homePos;

        private void Awake()
        {
            _grab = GetComponent<XRGrabInteractable>();
            _grab.selectExited.AddListener(OnReleased);
        }

        public void Inject(BattleDirector director, BattleTableView table)
        {
            _director = director;
            _table = table;
        }

        public void SetJob(JobType job)
        {
            if (body == null) return;
            body.material.color = job switch
            {
                JobType.Knight => knightColor,
                JobType.WhiteMage => healerColor,
                JobType.BlackMage => mageColor,
                JobType.Bard => bardColor,
                _ => Color.white
            };
        }

        private void OnReleased(SelectExitEventArgs _)
        {
            if (_director == null || _table == null) return;
            if (_director.State.Phase != BattlePhase.Move) return;

            var local = _table.transform.InverseTransformPoint(transform.position);
            var x = Mathf.RoundToInt(local.x / 0.12f + 3);
            var y = Mathf.RoundToInt(local.z / 0.12f + 3);
            var dest = new GridPos(x, y);

            if (_director.TryMove(UnitId, dest))
                transform.position = _table.GridToWorld(dest.X, dest.Y);
            else
                transform.position = _table.GridToWorld(_homePos.X, _homePos.Y);
        }

        public void RememberHome(GridPos pos) => _homePos = pos;
    }
}
