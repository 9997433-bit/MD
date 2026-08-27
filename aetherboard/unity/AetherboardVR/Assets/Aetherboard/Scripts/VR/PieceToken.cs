using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Piece token — supports VR grab (when XRI present) and desktop click-drag.
    /// </summary>
    public class PieceToken : MonoBehaviour
    {
        [SerializeField] private Renderer body;
        [SerializeField] private Color knightColor = new(0.2f, 0.5f, 0.8f);
        [SerializeField] private Color healerColor = new(0.2f, 0.7f, 0.35f);
        [SerializeField] private Color mageColor = new(0.55f, 0.25f, 0.75f);
        [SerializeField] private Color bardColor = new(0.85f, 0.45f, 0.1f);

        public string UnitId { get; set; }
        public bool IsSelected { get; private set; }

        private BattleDirector _director;
        private BattleTableView _table;
        private GridPos _homePos;
        private Vector3 _dragOffset;
        private bool _dragging;
        private Transform _coopBadge;
        private int _coopPlayer;

        public void InitProcedural(Renderer renderer)
        {
            body = renderer;
        }

        public void Inject(BattleDirector director, BattleTableView table)
        {
            _director = director;
            _table = table;
            TryWireXRGrab();
        }

        private void TryWireXRGrab()
        {
            var grabType = System.Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.Interactables.XRGrabInteractable, Unity.XR.Interaction.Toolkit");
            if (grabType == null) return;
            var grab = gameObject.GetComponent(grabType);
            if (grab == null) grab = gameObject.AddComponent(grabType);
            // XR release handled via DesktopBattleInput fallback when no XR rig
        }

        private Color _baseColor;
        private bool _hasBaseColor;

        public void SetJob(JobType job)
        {
            if (body == null) body = GetComponentInChildren<Renderer>();
            if (body == null) return;
            _baseColor = job switch
            {
                JobType.Knight => knightColor,
                JobType.WhiteMage => healerColor,
                JobType.BlackMage => mageColor,
                JobType.Bard => bardColor,
                _ => Color.white
            };
            _hasBaseColor = true;
            if (body.material == null) body.material = ProceduralAssets.CreateUnlitMaterial(_baseColor);
            else body.material.color = _baseColor;
        }

        public void SetCoopPlayer(int player)
        {
            _coopPlayer = player;
            if (player <= 0)
            {
                if (_coopBadge != null) _coopBadge.gameObject.SetActive(false);
                return;
            }

            if (_coopBadge == null)
            {
                var badgeGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
                badgeGo.name = "CoopBadge";
                badgeGo.transform.SetParent(transform, false);
                badgeGo.transform.localPosition = new Vector3(0, 0.14f, 0);
                badgeGo.transform.localScale = Vector3.one * 0.035f;
                var col = badgeGo.GetComponent<Collider>();
                if (col != null) Destroy(col);
                _coopBadge = badgeGo.transform;
            }

            _coopBadge.gameObject.SetActive(true);
            var color = player == 1 ? new Color(0.3f, 0.6f, 1f) : new Color(1f, 0.45f, 0.35f);
            _coopBadge.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(color);
        }

        public void SetSelected(bool selected)
        {
            IsSelected = selected;
            if (body == null || !_hasBaseColor) return;
            var tint = _coopPlayer > 0
                ? Color.Lerp(_baseColor, _coopPlayer == 1 ? new Color(0.3f, 0.6f, 1f) : new Color(1f, 0.45f, 0.35f), 0.15f)
                : _baseColor;
            body.material.color = selected
                ? Color.Lerp(tint, Color.white, 0.35f)
                : tint;
        }

        public void BeginDrag(Vector3 hitPoint)
        {
            _dragging = true;
            _dragOffset = transform.position - hitPoint;
        }

        public void DragTo(Vector3 hitPoint)
        {
            if (!_dragging) return;
            transform.position = hitPoint + _dragOffset;
        }

        public void EndDrag()
        {
            if (!_dragging) return;
            _dragging = false;
            if (_director == null || _table == null) return;
            if (_director.State.Phase != BattlePhase.Move) return;

            var dest = _table.WorldToGrid(transform.position);
            if (_director.TryMove(UnitId, dest))
                SnapToGrid(dest);
            else
                SnapToGrid(_homePos);
        }

        public void SnapToGrid(GridPos pos)
        {
            if (_table == null) return;
            transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * (_table.CellSize * 0.28f);
        }

        public void RememberHome(GridPos pos) => _homePos = pos;
    }
}
