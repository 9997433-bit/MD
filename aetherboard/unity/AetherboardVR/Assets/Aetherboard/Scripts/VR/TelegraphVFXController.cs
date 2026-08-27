using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class TelegraphVFXController : MonoBehaviour
    {
        [SerializeField] private GameObject previewRingPrefab;
        [SerializeField] private Transform vfxRoot;

        private readonly List<GameObject> _active = new();
        private BattleTableView _table;

        public void InitializeProcedural(BattleTableView table)
        {
            _table = table;
            vfxRoot = new GameObject("TelegraphVFX").transform;
            vfxRoot.SetParent(table.transform, false);
        }

        public void ShowPreview(List<GridPos> cells, TelegraphKind telegraph)
        {
            Clear();
            if (cells == null || _table == null) return;
            foreach (var pos in cells)
            {
                GameObject ring;
                if (previewRingPrefab != null)
                {
                    ring = Instantiate(previewRingPrefab, vfxRoot);
                }
                else
                {
                    ring = ProceduralAssets.CreatePreviewRing(vfxRoot, _table.CellSize);
                    var r = ring.GetComponent<Renderer>();
                    if (r != null)
                    {
                        r.material = ProceduralAssets.CreateUnlitMaterial(new Color(1f, 0.65f, 0.1f, 0.85f));
                    }
                }
                ring.transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.03f;
                _active.Add(ring);
            }
        }

        public void Clear()
        {
            foreach (var go in _active)
                if (go != null) Destroy(go);
            _active.Clear();
        }
    }
}
