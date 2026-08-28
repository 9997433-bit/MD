using UnityEngine;
using CosmicFront.Core;
using CosmicFront.UI;

namespace CosmicFront.Modes
{
    /// <summary>
    /// Tints the capture-point mesh by current Owner (Terran green / Orbital purple / None gray).
    /// </summary>
    [RequireComponent(typeof(CapturePoint))]
    public class CapturePointVisual : MonoBehaviour
    {
        private static readonly Color TerranColor = new Color(0.2f, 0.85f, 0.35f, 1f);
        private static readonly Color OrbitalColor = new Color(0.7f, 0.35f, 0.95f, 1f);
        private static readonly Color NoneColor = new Color(0.55f, 0.55f, 0.58f, 1f);

        [SerializeField] private Renderer targetRenderer;

        private CapturePoint _point;
        private TeamId _applied = (TeamId)(-1);
        private MaterialPropertyBlock _block;

        private void Awake()
        {
            _point = GetComponent<CapturePoint>();
            if (targetRenderer == null)
            {
                targetRenderer = GetComponent<Renderer>();
            }

            if (targetRenderer == null)
            {
                targetRenderer = GetComponentInChildren<Renderer>();
            }

            _block = new MaterialPropertyBlock();

            if (GetComponent<CapturePointWorldLabel>() == null)
            {
                gameObject.AddComponent<CapturePointWorldLabel>();
            }

            Apply(_point != null ? _point.Owner : TeamId.None);
        }

        private void LateUpdate()
        {
            if (_point == null) return;
            var owner = _point.Owner;
            if (owner == _applied) return;
            Apply(owner);
        }

        private void Apply(TeamId owner)
        {
            _applied = owner;
            var color = ColorFor(owner);
            if (targetRenderer == null) return;

            targetRenderer.GetPropertyBlock(_block);
            _block.SetColor("_Color", color);
            _block.SetColor("_BaseColor", color);
            targetRenderer.SetPropertyBlock(_block);

            // Prototype cylinders use the built-in default material; tint the instance too.
            var mat = targetRenderer.material;
            if (mat != null && mat.HasProperty("_Color"))
            {
                mat.color = color;
            }
        }

        public static Color ColorFor(TeamId owner)
        {
            switch (owner)
            {
                case TeamId.Terran: return TerranColor;
                case TeamId.Orbital: return OrbitalColor;
                default: return NoneColor;
            }
        }
    }
}
