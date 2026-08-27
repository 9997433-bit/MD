using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Telegraph preview rings and resolve-time VFX (slam, gale column, shrink wall).
    /// </summary>
    public class TelegraphVFXController : MonoBehaviour
    {
        [SerializeField] private GameObject previewRingPrefab;
        [SerializeField] private GameObject furyCastBar;
        [SerializeField] private Transform vfxRoot;

        private readonly List<GameObject> _active = new();

        public void ShowPreview(List<GridPos> cells, TelegraphKind telegraph)
        {
            Clear();
            if (cells == null) return;
            foreach (var pos in cells)
            {
                var ring = Instantiate(previewRingPrefab, vfxRoot);
                ring.transform.localPosition = new Vector3(pos.X * 0.12f, 0.01f, pos.Y * 0.12f);
                _active.Add(ring);
            }
            if (furyCastBar != null)
                furyCastBar.SetActive(telegraph is TelegraphKind.EarthenFury or TelegraphKind.Cyclone);
        }

        public void Clear()
        {
            foreach (var go in _active)
                if (go != null) Destroy(go);
            _active.Clear();
            if (furyCastBar != null) furyCastBar.SetActive(false);
        }
    }
}
