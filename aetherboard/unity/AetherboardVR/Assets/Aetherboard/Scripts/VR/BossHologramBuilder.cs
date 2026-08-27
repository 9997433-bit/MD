using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Procedural boss hologram mesh + world-space labels (earth / wind themes).
    /// </summary>
    public class BossHologramBuilder : MonoBehaviour
    {
        private Transform _coreRoot;
        private Transform _outerRing;
        private Transform _innerRing;
        private Transform _nameplate;
        private TextMesh _nameLabel;
        private TextMesh _statsLabel;
        private TextMesh _castLabel;
        private Renderer _coreRenderer;
        private Light _hologramLight;
        private string _bossId = "earth";
        private float _spinSpeed;

        public void BuildLocal()
        {
            TryLoadExternalModel(_bossId);
            if (_coreRoot == null)
                BuildProceduralCore();

            BuildRings();
            BuildNameplate();
            BuildLight();
            ApplyTheme(_bossId);
        }

        public void ApplyTheme(string bossId)
        {
            var newId = string.IsNullOrEmpty(bossId) ? "earth" : bossId;
            if (newId != _bossId)
            {
                _bossId = newId;
                ClearCore();
                TryLoadExternalModel(_bossId);
                if (_coreRoot == null)
                    BuildProceduralCore();
            }

            var palette = PaletteForBoss(_bossId);

            if (_coreRenderer != null)
                _coreRenderer.sharedMaterial = BattleArtPalette.CreateEmissiveMaterial(palette, 1.4f);

            if (_outerRing != null)
                _outerRing.GetComponent<Renderer>().sharedMaterial =
                    BattleArtPalette.CreateEmissiveMaterial(palette, 0.7f);
            if (_innerRing != null)
                _innerRing.GetComponent<Renderer>().sharedMaterial =
                    BattleArtPalette.CreateEmissiveMaterial(Color.Lerp(palette, Color.white, 0.25f), 0.5f);

            if (_hologramLight != null)
                _hologramLight.color = palette;
        }

        public void UpdateState(BossState boss, string bossId)
        {
            if (boss == null) return;
            ApplyTheme(bossId);

            var hpRatio = boss.MaxHp > 0 ? boss.Hp / (float)boss.MaxHp : 1f;
            transform.localScale = Vector3.one * (0.85f + 0.35f * hpRatio);

            _spinSpeed = boss.FuryCastTurns > 0 ? (boss.FuryCastTurns == 1 ? 95f : 55f) : 12f;

            if (_nameLabel != null) _nameLabel.text = boss.Name;
            if (_statsLabel != null)
                _statsLabel.text = $"HP {boss.Hp}/{boss.MaxHp}   Phase {boss.Phase}";
            if (_castLabel != null)
            {
                var casting = boss.FuryCastTurns > 0;
                _castLabel.gameObject.SetActive(casting);
                if (casting)
                    _castLabel.text = boss.FuryCastTurns == 1
                        ? $"!! 读条 {boss.FuryCastTurns} !!"
                        : $"读条 {boss.FuryCastTurns}";
            }

            PulseRings(boss);
        }

        public void Tick(float deltaTime)
        {
            if (_coreRoot != null)
                _coreRoot.Rotate(Vector3.up, _spinSpeed * deltaTime, Space.Self);
            if (_outerRing != null)
                _outerRing.Rotate(Vector3.up, -_spinSpeed * 0.6f * deltaTime, Space.Self);
            if (_innerRing != null)
                _innerRing.Rotate(Vector3.right, _spinSpeed * 0.4f * deltaTime, Space.Self);
            FaceNameplateToCamera();
        }

        private void TryLoadExternalModel(string bossId)
        {
            var external = BattleArtCatalog.LoadBossHologram(bossId);
            if (external == null) return;

            var inst = Instantiate(external, transform);
            inst.transform.localPosition = Vector3.zero;
            inst.transform.localRotation = Quaternion.identity;
            _coreRoot = inst.transform;
            _coreRenderer = inst.GetComponentInChildren<Renderer>();
        }

        private void ClearCore()
        {
            if (_coreRoot == null) return;
            Destroy(_coreRoot.gameObject);
            _coreRoot = null;
            _coreRenderer = null;
        }

        private void BuildProceduralCore()
        {
            _coreRoot = new GameObject("Core").transform;
            _coreRoot.SetParent(transform, false);

            if (_bossId == "wind")
            {
                var body = CreatePrimitive(PrimitiveType.Capsule, _coreRoot, "WindBody",
                    new Vector3(0.12f, 0.16f, 0.12f), Vector3.zero);
                var swirl = CreatePrimitive(PrimitiveType.Cylinder, _coreRoot, "Swirl",
                    new Vector3(0.2f, 0.01f, 0.2f), new Vector3(0, 0.08f, 0));
                swirl.transform.localRotation = Quaternion.Euler(15, 0, 0);
                _coreRenderer = body.GetComponent<Renderer>();
            }
            else
            {
                var body = CreatePrimitive(PrimitiveType.Sphere, _coreRoot, "EarthCore",
                    new Vector3(0.16f, 0.16f, 0.16f), Vector3.zero);
                var chip = CreatePrimitive(PrimitiveType.Cube, _coreRoot, "Shard",
                    new Vector3(0.08f, 0.1f, 0.04f), new Vector3(0.06f, 0.04f, 0.05f));
                chip.transform.localRotation = Quaternion.Euler(20, 30, 10);
                _coreRenderer = body.GetComponent<Renderer>();
            }
        }

        private void BuildRings()
        {
            if (_outerRing != null) return;
            _outerRing = CreatePrimitive(PrimitiveType.Cylinder, transform, "OuterRing",
                new Vector3(0.28f, 0.006f, 0.28f), new Vector3(0, -0.02f, 0)).transform;
            _innerRing = CreatePrimitive(PrimitiveType.Cylinder, transform, "InnerRing",
                new Vector3(0.2f, 0.004f, 0.2f), new Vector3(0, 0.02f, 0)).transform;
        }

        private void BuildNameplate()
        {
            if (_nameplate != null) return;

            _nameplate = new GameObject("Nameplate").transform;
            _nameplate.SetParent(transform, false);
            _nameplate.localPosition = new Vector3(0, 0.32f, 0);

            var bg = CreatePrimitive(PrimitiveType.Quad, _nameplate, "PlateBg",
                new Vector3(0.42f, 0.18f, 1f), Vector3.zero);
            bg.GetComponent<Renderer>().sharedMaterial =
                BattleArtPalette.CreateSurfaceMaterial(new Color(0.05f, 0.08f, 0.12f, 0.85f), 0.2f, 0.3f);

            _nameLabel = CreateText(_nameplate, "Name", new Vector3(0, 0.05f, -0.01f), 32, TextAnchor.MiddleCenter);
            _statsLabel = CreateText(_nameplate, "Stats", new Vector3(0, -0.02f, -0.01f), 24, TextAnchor.MiddleCenter);
            _castLabel = CreateText(_nameplate, "Cast", new Vector3(0, -0.07f, -0.01f), 26, TextAnchor.MiddleCenter);
            _castLabel.color = new Color(1f, 0.45f, 0.2f);
            _castLabel.gameObject.SetActive(false);
        }

        private void BuildLight()
        {
            if (_hologramLight != null) return;
            var lightGo = new GameObject("HologramLight");
            lightGo.transform.SetParent(transform, false);
            lightGo.transform.localPosition = new Vector3(0, 0.1f, 0);
            _hologramLight = lightGo.AddComponent<Light>();
            _hologramLight.type = LightType.Point;
            _hologramLight.range = 1.2f;
            _hologramLight.intensity = 0.85f;
            _hologramLight.shadows = LightShadows.None;
        }

        private void PulseRings(BossState boss)
        {
            if (_outerRing == null) return;
            var urgent = boss.FuryCastTurns == 1;
            var pulse = urgent ? 1f + Mathf.Sin(Time.time * 10f) * 0.08f : 1f;
            _outerRing.localScale = new Vector3(0.28f * pulse, 0.006f, 0.28f * pulse);
        }

        private void FaceNameplateToCamera()
        {
            if (_nameplate == null) return;
            var cam = Camera.main;
            if (cam == null) return;
            _nameplate.rotation = Quaternion.LookRotation(
                _nameplate.position - cam.transform.position,
                Vector3.up);
        }

        private static GameObject CreatePrimitive(
            PrimitiveType type, Transform parent, string name, Vector3 scale, Vector3 localPos)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localScale = scale;
            go.transform.localPosition = localPos;
            var col = go.GetComponent<Collider>();
            if (col != null) Destroy(col);
            return go;
        }

        private static TextMesh CreateText(
            Transform parent, string name, Vector3 localPos, int fontSize, TextAnchor anchor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            var text = go.AddComponent<TextMesh>();
            text.fontSize = fontSize;
            text.characterSize = 0.02f;
            text.anchor = anchor;
            text.alignment = TextAlignment.Center;
            text.color = Color.white;
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            return text;
        }

        private static Color PaletteForBoss(string bossId) => bossId switch
        {
            "wind" => new Color(0.4f, 0.78f, 1f),
            _ => new Color(0.92f, 0.32f, 0.12f)
        };
    }
}
