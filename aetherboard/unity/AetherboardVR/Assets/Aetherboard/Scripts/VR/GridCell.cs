using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class GridCell : MonoBehaviour
    {
        [SerializeField] private Renderer surface;
        [SerializeField] private Color normalColor = new(0.15f, 0.2f, 0.28f);
        [SerializeField] private Color hazardColor = new(0.45f, 0.1f, 0.1f);
        [SerializeField] private Color previewColor = new(0.7f, 0.45f, 0.1f);
        [SerializeField] private Color bossColor = new(0.35f, 0.12f, 0.12f);

        public int X { get; private set; }
        public int Y { get; private set; }

        public void Init(int x, int y)
        {
            X = x;
            Y = y;
            var isBoss = x == BoardMath.BossPos(BoardMath.DefaultSize).X &&
                         y == BoardMath.BossPos(BoardMath.DefaultSize).Y;
            if (isBoss) SetColor(bossColor);
        }

        public void SetKind(CellKind kind, bool preview)
        {
            if (preview) SetColor(previewColor);
            else if (kind == CellKind.Hazard) SetColor(hazardColor);
            else SetColor(normalColor);
        }

        private void SetColor(Color c)
        {
            if (surface != null)
            {
                surface.material.color = c;
            }
        }
    }
}
