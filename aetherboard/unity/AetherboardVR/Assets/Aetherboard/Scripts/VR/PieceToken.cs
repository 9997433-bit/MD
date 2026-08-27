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
        private bool _xrGrabbing;
        private Transform _coopBadge;
        private int _coopPlayer;
        private GridSnapHighlighter _highlighter;
        private CoopController _coop;

        public bool IsBeingManipulated => _dragging || _xrGrabbing;

        public void InitProcedural(Renderer renderer)
        {
            body = renderer;
        }

        public void Inject(
            BattleDirector director,
            BattleTableView table,
            GridSnapHighlighter highlighter = null,
            CoopController coop = null)
        {
            _director = director;
            _table = table;
            _highlighter = highlighter;
            _coop = coop;

            var grab = GetComponent<PieceXRGrabController>();
            if (grab == null) grab = gameObject.AddComponent<PieceXRGrabController>();
            grab.Setup(this, director, table, coop, highlighter);
            EnsureCollider();
        }

        private void EnsureCollider()
        {
            if (GetComponent<Collider>() != null) return;
            var box = gameObject.AddComponent<BoxCollider>();
            box.center = new Vector3(0, 0.05f, 0);
            box.size = new Vector3(0.08f, 0.1f, 0.08f);
        }

        public void SetGrabbing(bool grabbing) => _xrGrabbing = grabbing;

        private Color _baseColor;
        private bool _hasBaseColor;

        public void SetJob(JobType job)
        {
            var builder = GetComponent<PieceVisualBuilder>();
            if (builder != null)
            {
                builder.Apply(job);
                body = builder.PrimaryRenderer ?? body;
                _baseColor = BattleArtPalette.ForJob(job);
                _hasBaseColor = body != null;
                if (body != null && body.material != null)
                    body.material.color = _baseColor;
                return;
            }

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
            if (body.material == null) body.material = BattleArtPalette.CreateSurfaceMaterial(_baseColor);
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
            if (_coop != null && !_coop.CanControlUnit(UnitId)) return;
            _dragging = true;
            _dragOffset = transform.position - hitPoint;
            SetSelected(true);
            _highlighter?.Begin(_table, _table != null ? _table.CellSize * 0.28f : 0.03f);
        }

        public void DragTo(Vector3 hitPoint)
        {
            if (!_dragging) return;
            transform.position = hitPoint + _dragOffset;
            if (_table != null)
                _highlighter?.SetHover(_table.WorldToGrid(transform.position));
        }

        public void EndDrag()
        {
            if (!_dragging) return;
            _dragging = false;
            _highlighter?.End();
            if (_director == null || _table == null)
            {
                SetSelected(false);
                return;
            }

            if (_director.State.Phase != BattlePhase.Move)
            {
                SnapToGrid(_homePos);
                SetSelected(false);
                return;
            }

            var dest = _table.WorldToGrid(transform.position);
            if (_director.TryMove(UnitId, dest))
                SnapToGrid(dest);
            else
                SnapToGrid(_homePos);
            SetSelected(false);
        }

        public void SnapToGrid(GridPos pos)
        {
            if (_table == null) return;
            transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * (_table.CellSize * 0.28f);
        }

        public void RememberHome(GridPos pos) => _homePos = pos;
    }
}
