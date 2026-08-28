using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Enhanced telegraph VFX: preview rings, shrink walls, slam shockwaves, wind/spread/stack markers.
    /// </summary>
    public class TelegraphVFXController : MonoBehaviour
    {
        [SerializeField] private GameObject previewRingPrefab;
        [SerializeField] private Transform vfxRoot;

        private readonly List<GameObject> _active = new();
        private readonly List<Material> _pulseMaterials = new();
        private BattleTableView _table;
        private Coroutine _pulseRoutine;

        public void InitializeProcedural(BattleTableView table)
        {
            _table = table;
            previewRingPrefab = previewRingPrefab != null
                ? previewRingPrefab
                : BattlePrefabLibrary.PreviewRingPrefab;
            vfxRoot = new GameObject("TelegraphVFX").transform;
            vfxRoot.SetParent(table.transform, false);
        }

        public void ShowPreview(List<GridPos> cells, TelegraphKind telegraph)
        {
            Clear();
            if (cells == null || _table == null) return;

            var ringColor = ColorForTelegraph(telegraph);
            foreach (var pos in cells)
            {
                var ring = CreateRing(pos, ringColor);
                _active.Add(ring);
            }

            switch (telegraph)
            {
                case TelegraphKind.Shrink:
                    SpawnShrinkWalls(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(3.5f, 0.12f));
                    break;
                case TelegraphKind.Slam:
                    _pulseRoutine = StartCoroutine(SlamShockwave(cells));
                    break;
                case TelegraphKind.Earthquake:
                    SpawnEarthquakeCracks(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(2.5f, 0.06f));
                    break;
                case TelegraphKind.Gale:
                    SpawnGaleLine(cells);
                    break;
                case TelegraphKind.Spread:
                    _pulseRoutine = StartCoroutine(PulseActive(2f, 0.1f));
                    break;
                case TelegraphKind.Stack:
                    SpawnStackBeacon(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(1.8f, 0.14f));
                    break;
                case TelegraphKind.EarthenFury:
                case TelegraphKind.Cyclone:
                case TelegraphKind.Blizzard:
                case TelegraphKind.Eruption:
                    _pulseRoutine = StartCoroutine(FuryPulse());
                    break;
                case TelegraphKind.IceLance:
                    SpawnIceCross(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(2.2f, 0.08f));
                    break;
                case TelegraphKind.FrozenGround:
                    SpawnFrozenGround(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(2.4f, 0.07f));
                    break;
                case TelegraphKind.IceRing:
                    SpawnIceRing(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(2f, 0.1f));
                    break;
                case TelegraphKind.FlameBreath:
                    SpawnFlameX(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(2.3f, 0.09f));
                    break;
                case TelegraphKind.Meteor:
                    SpawnMeteorMarkers(cells);
                    _pulseRoutine = StartCoroutine(PulseActive(2.6f, 0.1f));
                    break;
                case TelegraphKind.HeatLink:
                    _pulseRoutine = StartCoroutine(PulseActive(2f, 0.12f));
                    break;
            }
        }

        private static Color ColorForTelegraph(TelegraphKind telegraph) => telegraph switch
        {
            TelegraphKind.Shrink => new Color(0.55f, 0.2f, 0.95f, 0.9f),
            TelegraphKind.Slam => new Color(1f, 0.25f, 0.1f, 0.9f),
            TelegraphKind.Earthquake => new Color(1f, 0.55f, 0.1f, 0.85f),
            TelegraphKind.Gale => new Color(0.4f, 0.85f, 1f, 0.9f),
            TelegraphKind.Spread => new Color(1f, 0.5f, 0.15f, 0.9f),
            TelegraphKind.Stack => new Color(0.25f, 0.95f, 0.55f, 0.9f),
            TelegraphKind.EarthenFury => new Color(1f, 0.15f, 0.1f, 0.95f),
            TelegraphKind.Cyclone => new Color(0.7f, 0.85f, 1f, 0.95f),
            TelegraphKind.IceLance => new Color(0.55f, 0.85f, 1f, 0.92f),
            TelegraphKind.FrozenGround => new Color(0.35f, 0.65f, 1f, 0.88f),
            TelegraphKind.IceRing => new Color(0.65f, 0.92f, 1f, 0.9f),
            TelegraphKind.Blizzard => new Color(0.75f, 0.9f, 1f, 0.95f),
            TelegraphKind.FlameBreath => new Color(1f, 0.35f, 0.08f, 0.92f),
            TelegraphKind.Meteor => new Color(1f, 0.45f, 0.12f, 0.9f),
            TelegraphKind.HeatLink => new Color(1f, 0.55f, 0.2f, 0.9f),
            TelegraphKind.Eruption => new Color(1f, 0.2f, 0.05f, 0.95f),
            _ => new Color(1f, 0.65f, 0.1f, 0.85f)
        };

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
                var mat = ProceduralAssets.CreateUnlitMaterial(color);
                ring.GetComponent<Renderer>().material = mat;
                _pulseMaterials.Add(mat);
            }
            ring.transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.03f;
            return ring;
        }

        private void SpawnShrinkWalls(List<GridPos> cells)
        {
            var center = _table.GridToWorld(3, 3);
            var wallColor = new Color(0.45f, 0.15f, 0.85f, 0.75f);
            foreach (var pos in cells)
            {
                var world = _table.GridToWorld(pos.X, pos.Y);
                var inward = (center - world);
                inward.y = 0;
                if (inward.sqrMagnitude < 0.001f) continue;
                inward.Normalize();
                var wall = ProceduralAssets.CreateWallQuad(vfxRoot, _table.CellSize * 0.92f, 0.06f, wallColor);
                wall.transform.position = world + Vector3.up * 0.03f;
                wall.transform.rotation = Quaternion.LookRotation(inward, Vector3.up);
                _active.Add(wall);
            }
        }

        private void SpawnEarthquakeCracks(List<GridPos> cells)
        {
            var crackColor = new Color(1f, 0.35f, 0.1f, 0.95f);
            foreach (var pos in cells)
            {
                var center = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.025f;
                _active.Add(CreateCrackLine(center, _table.CellSize * 0.42f, crackColor, 0));
                _active.Add(CreateCrackLine(center, _table.CellSize * 0.35f, crackColor, 90f));
            }
        }

        private void SpawnGaleLine(List<GridPos> cells)
        {
            if (cells.Count == 0) return;
            var boss = _table.GridToWorld(3, 3);
            var end = _table.GridToWorld(cells[0].X, cells[0].Y);
            for (var i = 1; i < cells.Count; i++)
            {
                var p = _table.GridToWorld(cells[i].X, cells[i].Y);
                if ((p - boss).sqrMagnitude > (end - boss).sqrMagnitude) end = p;
            }
            var go = new GameObject("GaleLine");
            go.transform.SetParent(vfxRoot, false);
            var line = go.AddComponent<LineRenderer>();
            line.positionCount = 2;
            line.startWidth = 0.015f;
            line.endWidth = 0.006f;
            var color = new Color(0.35f, 0.9f, 1f, 0.95f);
            line.material = ProceduralAssets.CreateUnlitMaterial(color);
            line.startColor = color;
            line.endColor = color;
            line.useWorldSpace = true;
            line.SetPosition(0, boss + Vector3.up * 0.05f);
            line.SetPosition(1, end + Vector3.up * 0.05f);
            _active.Add(go);
        }

        private void SpawnStackBeacon(List<GridPos> cells)
        {
            var center = cells.Count > 0
                ? _table.GridToWorld(cells[0].X, cells[0].Y)
                : _table.GridToWorld(3, 3);
            var pillar = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pillar.name = "StackBeacon";
            pillar.transform.SetParent(vfxRoot, false);
            pillar.transform.position = center + Vector3.up * 0.04f;
            pillar.transform.localScale = new Vector3(_table.CellSize * 0.35f, 0.002f, _table.CellSize * 0.35f);
            pillar.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(0.2f, 1f, 0.55f, 0.55f));
            Destroy(pillar.GetComponent<Collider>());
            _active.Add(pillar);
        }

        private void SpawnIceCross(List<GridPos> cells)
        {
            if (cells.Count == 0) return;
            var boss = _table.GridToWorld(3, 2);
            var iceColor = new Color(0.45f, 0.85f, 1f, 0.95f);
            var horiz = new GameObject("IceLanceH");
            horiz.transform.SetParent(vfxRoot, false);
            var hLine = horiz.AddComponent<LineRenderer>();
            hLine.positionCount = 2;
            hLine.startWidth = 0.012f;
            hLine.endWidth = 0.005f;
            hLine.material = ProceduralAssets.CreateUnlitMaterial(iceColor);
            hLine.startColor = hLine.endColor = iceColor;
            hLine.useWorldSpace = true;
            hLine.SetPosition(0, _table.GridToWorld(0, 2) + Vector3.up * 0.04f);
            hLine.SetPosition(1, _table.GridToWorld(6, 2) + Vector3.up * 0.04f);
            _active.Add(horiz);

            var vert = new GameObject("IceLanceV");
            vert.transform.SetParent(vfxRoot, false);
            var vLine = vert.AddComponent<LineRenderer>();
            vLine.positionCount = 2;
            vLine.startWidth = 0.012f;
            vLine.endWidth = 0.005f;
            vLine.material = ProceduralAssets.CreateUnlitMaterial(iceColor);
            vLine.startColor = vLine.endColor = iceColor;
            vLine.useWorldSpace = true;
            vLine.SetPosition(0, _table.GridToWorld(3, 0) + Vector3.up * 0.04f);
            vLine.SetPosition(1, _table.GridToWorld(3, 6) + Vector3.up * 0.04f);
            _active.Add(vert);
        }

        private void SpawnFrozenGround(List<GridPos> cells)
        {
            var frostColor = new Color(0.4f, 0.75f, 1f, 0.85f);
            foreach (var pos in cells)
            {
                var slab = GameObject.CreatePrimitive(PrimitiveType.Cube);
                slab.name = "FrozenSlab";
                slab.transform.SetParent(vfxRoot, false);
                slab.transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.02f;
                slab.transform.localScale = new Vector3(_table.CellSize * 0.88f, 0.003f, _table.CellSize * 0.88f);
                slab.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(frostColor);
                Destroy(slab.GetComponent<Collider>());
                _active.Add(slab);
            }
        }

        private void SpawnIceRing(List<GridPos> cells)
        {
            var ringColor = new Color(0.55f, 0.9f, 1f, 0.75f);
            var center = _table.GridToWorld(3, 3);
            var ring = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            ring.name = "IceRing";
            ring.transform.SetParent(vfxRoot, false);
            ring.transform.position = center + Vector3.up * 0.025f;
            ring.transform.localScale = new Vector3(_table.CellSize * 1.05f, 0.003f, _table.CellSize * 1.05f);
            ring.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(ringColor);
            Destroy(ring.GetComponent<Collider>());
            _active.Add(ring);
        }

        private void SpawnFlameX(List<GridPos> cells)
        {
            var fireColor = new Color(1f, 0.4f, 0.1f, 0.95f);
            var center = _table.GridToWorld(3, 3) + Vector3.up * 0.04f;
            foreach (var (dx, dy) in new[] { (1, 1), (1, -1) })
            {
                var line = new GameObject("FlameDiag");
                line.transform.SetParent(vfxRoot, false);
                var lr = line.AddComponent<LineRenderer>();
                lr.positionCount = 2;
                lr.startWidth = 0.012f;
                lr.endWidth = 0.005f;
                lr.material = ProceduralAssets.CreateUnlitMaterial(fireColor);
                lr.startColor = lr.endColor = fireColor;
                lr.useWorldSpace = true;
                lr.SetPosition(0, _table.GridToWorld(3 - 3 * dx, 3 - 3 * dy) + Vector3.up * 0.04f);
                lr.SetPosition(1, _table.GridToWorld(3 + 3 * dx, 3 + 3 * dy) + Vector3.up * 0.04f);
                _active.Add(line);
            }
            _ = center;
        }

        private void SpawnMeteorMarkers(List<GridPos> cells)
        {
            var meteorColor = new Color(1f, 0.35f, 0.08f, 0.9f);
            foreach (var pos in cells)
            {
                var marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                marker.name = "MeteorMarker";
                marker.transform.SetParent(vfxRoot, false);
                marker.transform.position = _table.GridToWorld(pos.X, pos.Y) + Vector3.up * 0.06f;
                marker.transform.localScale = Vector3.one * (_table.CellSize * 0.28f);
                marker.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(meteorColor);
                Destroy(marker.GetComponent<Collider>());
                _active.Add(marker);
            }
        }

        private static GameObject CreateCrackLine(Vector3 center, float halfLen, Color color, float yawDeg)
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
            var rot = Quaternion.Euler(0, yawDeg, 0);
            var dir = rot * Vector3.right * halfLen;
            line.SetPosition(0, center - dir);
            line.SetPosition(1, center + dir);
            return go;
        }

        private System.Collections.IEnumerator PulseActive(float speed, float amplitude)
        {
            var pulseTargets = new List<(Transform transform, Vector3 baseScale)>();
            foreach (var go in _active)
            {
                if (go == null || go.name.Contains("Wall") || go.name.Contains("Gale") ||
                    go.name.Contains("Crack") || go.name.Contains("Slam"))
                    continue;
                pulseTargets.Add((go.transform, go.transform.localScale));
            }

            while (true)
            {
                var pulse = 1f + Mathf.Sin(Time.time * speed) * amplitude;
                foreach (var (t, baseScale) in pulseTargets)
                {
                    if (t == null) continue;
                    t.localScale = new Vector3(baseScale.x * pulse, baseScale.y, baseScale.z * pulse);
                }
                foreach (var mat in _pulseMaterials)
                {
                    if (mat == null) continue;
                    var c = mat.color;
                    c.a = 0.65f + Mathf.Sin(Time.time * speed) * 0.25f;
                    mat.color = c;
                }
                yield return null;
            }
        }

        private System.Collections.IEnumerator FuryPulse()
        {
            while (true)
            {
                foreach (var go in _active)
                {
                    if (go == null) continue;
                    var s = 1f + Mathf.Sin(Time.time * 5f) * 0.15f;
                    go.transform.localScale = new Vector3(
                        _table.CellSize * 0.95f * s, 0.006f, _table.CellSize * 0.95f * s);
                }
                yield return null;
            }
        }

        private System.Collections.IEnumerator SlamShockwave(List<GridPos> cells)
        {
            var center = cells.Count > 0
                ? _table.GridToWorld(cells[0].X, cells[0].Y)
                : _table.GridToWorld(3, 3);

            for (var wave = 0; wave < 2; wave++)
            {
                var shock = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                shock.name = "SlamShockwave";
                shock.transform.SetParent(vfxRoot, false);
                shock.transform.position = center + Vector3.up * 0.02f;
                shock.transform.localScale = new Vector3(0.08f, 0.004f, 0.08f);
                var mat = ProceduralAssets.CreateUnlitMaterial(new Color(1f, 0.3f, 0.1f, 0.55f));
                shock.GetComponent<Renderer>().material = mat;
                Destroy(shock.GetComponent<Collider>());
                _active.Add(shock);

                for (var t = 0f; t < 0.9f; t += Time.deltaTime)
                {
                    var scale = Mathf.Lerp(0.08f, 0.55f, t / 0.9f);
                    shock.transform.localScale = new Vector3(scale, 0.004f, scale);
                    var c = mat.color;
                    c.a = Mathf.Lerp(0.55f, 0.05f, t / 0.9f);
                    mat.color = c;
                    yield return null;
                }
                if (wave == 0) yield return new WaitForSeconds(0.15f);
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
            _pulseMaterials.Clear();
        }
    }
}
