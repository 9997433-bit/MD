using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Enhanced telegraph VFX: preview rings + shrink wall pulse + slam shockwave.
    /// </summary>
    public class TelegraphVFXController : MonoBehaviour
    {
        [SerializeField] private GameObject previewRingPrefab;
        [SerializeField] private Transform vfxRoot;

        private readonly List<GameObject> _active = new();
        private BattleTableView _table;
        private Coroutine _pulseRoutine;

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
                var ring = CreateRing(pos, new Color(1f, 0.65f, 0.1f, 0.85f));
                _active.Add(ring);
            }

            if (telegraph == TelegraphKind.Shrink)
                _pulseRoutine = StartCoroutine(PulseShrinkWalls(cells));
            else if (telegraph == TelegraphKind.Slam)
                _pulseRoutine = StartCoroutine(SlamShockwave());
            else if (telegraph == TelegraphKind.Earthquake)
                SpawnEarthquakeCracks(cells);
        }

        private GameObject CreateRing(GridPos pos, Color color)
        {
            GameObject ring;
            if (previewRingPrefab != null)
            {
                ring = Instantiate(previewRingPrefab, vfxRoot);
            }
            else
            {
                ring = ProceduralAssets.CreatePreviewRing(vfxRoot, _table.CellSize);
                ring.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(color);
            }
            ring.transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.03f;
            return ring;
        }

        private IEnumerator PulseShrinkWalls(List<GridPos> cells)
        {
            while (true)
            {
                foreach (var go in _active)
                {
                    if (go == null) continue;
                    var s = 1f + Mathf.Sin(Time.time * 3f) * 0.08f;
                    go.transform.localScale = new Vector3(s, 1, s);
                }
                yield return null;
            }
        }

        private void SpawnEarthquakeCracks(List<GridPos> cells)
        {
            var crackColor = new Color(1f, 0.35f, 0.1f, 0.95f);
            foreach (var pos in cells)
            {
                var center = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.025f;
                var crack = CreateCrackLine(center, _table.CellSize * 0.42f, crackColor);
                _active.Add(crack);
            }
        }

        private static GameObject CreateCrackLine(Vector3 center, float halfLen, Color color)
        {
            var go = new GameObject("EarthquakeCrack");
            var line = go.AddComponent<LineRenderer>();
            line.positionCount = 2;
            line.startWidth = 0.008f;
            line.endWidth = 0.004f;
            line.material = ProceduralAssets.CreateUnlitMaterial(color);
            line.startColor = color;
            line.endColor = color;
            line.useWorldSpace = true;
            line.SetPosition(0, center + new Vector3(-halfLen, 0, 0));
            line.SetPosition(1, center + new Vector3(halfLen, 0, 0));
            return go;
        }

        private IEnumerator SlamShockwave()
        {
            var center = _table.GridToWorld(3, 3);
            var wave = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            wave.transform.SetParent(vfxRoot);
            wave.transform.position = center + Vector3.up * 0.02f;
            wave.transform.localScale = new Vector3(0.1f, 0.005f, 0.1f);
            wave.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(1f, 0.3f, 0.1f, 0.6f));
            Destroy(wave.GetComponent<Collider>());
            _active.Add(wave);

            for (var t = 0f; t < 1.2f; t += Time.deltaTime)
            {
                var scale = Mathf.Lerp(0.1f, 0.45f, t / 1.2f);
                wave.transform.localScale = new Vector3(scale, 0.005f, scale);
                yield return null;
            }
        }

        public void Clear()
        {
            if (_pulseRoutine != null)
            {
                StopCoroutine(_pulseRoutine);
                _pulseRoutine = null;
            }
            foreach (var go in _active)
                if (go != null) Destroy(go);
            _active.Clear();
        }
    }
}
