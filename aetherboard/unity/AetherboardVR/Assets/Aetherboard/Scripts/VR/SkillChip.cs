using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Single skill chip in the radial menu — supports hover highlight for VR ray.
    /// </summary>
    public class SkillChip : MonoBehaviour
    {
        [SerializeField] private Color gcdColor = new(0.2f, 0.55f, 0.95f);
        [SerializeField] private Color ogcdColor = new(0.9f, 0.55f, 0.1f);
        [SerializeField] private Color hoverTint = new(1f, 1f, 1f, 0.45f);
        [SerializeField] private Color disabledColor = new(0.35f, 0.35f, 0.35f, 0.65f);

        public string SkillId { get; set; }
        public bool IsEnabled { get; private set; } = true;

        private Renderer _renderer;
        private Color _baseColor;
        private Vector3 _baseScale;
        private bool _hovered;

        public void Init(Renderer renderer, string kind, bool enabled)
        {
            _renderer = renderer;
            IsEnabled = enabled;
            _baseColor = kind == "ogcd" ? ogcdColor : gcdColor;
            _baseScale = transform.localScale;
            ApplyColor(IsEnabled ? _baseColor : disabledColor);
        }

        public void SetHovered(bool hovered)
        {
            if (_hovered == hovered) return;
            _hovered = hovered;
            if (!IsEnabled)
            {
                ApplyColor(disabledColor);
                transform.localScale = _baseScale;
                return;
            }
            ApplyColor(hovered ? Color.Lerp(_baseColor, hoverTint, 0.55f) : _baseColor);
            transform.localScale = hovered
                ? new Vector3(_baseScale.x * 1.12f, _baseScale.y, _baseScale.z * 1.12f)
                : _baseScale;
        }

        private void ApplyColor(Color c)
        {
            if (_renderer == null) return;
            if (_renderer.material == null)
                _renderer.material = ProceduralAssets.CreateUnlitMaterial(c);
            else
                _renderer.material.color = c;
        }
    }
}
