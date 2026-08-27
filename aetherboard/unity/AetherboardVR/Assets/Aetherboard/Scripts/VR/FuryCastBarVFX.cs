using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Boss fury / cyclone cast bar with orbital warning rings and interrupt burst.
    /// </summary>
    public class FuryCastBarVFX : MonoBehaviour
    {
        private Transform _barRoot;
        private Transform _fill;
        private Transform _urgentGlow;
        private readonly List<Transform> _orbitRings = new();
        private BossState _boss;
        private string _bossId = "earth";
        private int _lastFuryTurns;
        private float _pulse;
        private Coroutine _interruptRoutine;

        public void Initialize(Transform parent)
        {
            _barRoot = new GameObject("FuryCastBar").transform;
            _barRoot.SetParent(parent, false);
            _barRoot.localPosition = new Vector3(0, 0.28f, 0);

            var bg = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bg.name = "BarBG";
            bg.transform.SetParent(_barRoot, false);
            bg.transform.localScale = new Vector3(0.38f, 0.028f, 0.045f);
            bg.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(0.1f, 0.1f, 0.12f, 0.9f));
            Destroy(bg.GetComponent<Collider>());

            var fillGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
            fillGo.name = "BarFill";
            fillGo.transform.SetParent(_barRoot, false);
            fillGo.transform.localScale = new Vector3(0.36f, 0.032f, 0.038f);
            _fill = fillGo.transform;
            _fill.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(0.95f, 0.15f, 0.1f));
            Destroy(fillGo.GetComponent<Collider>());

            _urgentGlow = GameObject.CreatePrimitive(PrimitiveType.Cube).transform;
            _urgentGlow.name = "UrgentGlow";
            _urgentGlow.SetParent(_barRoot, false);
            _urgentGlow.localScale = new Vector3(0.4f, 0.04f, 0.05f);
            _urgentGlow.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(1f, 0.2f, 0.1f, 0.35f));
            Destroy(_urgentGlow.GetComponent<Collider>());
            _urgentGlow.gameObject.SetActive(false);

            for (var i = 0; i < 3; i++)
            {
                var ring = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                ring.name = $"OrbitRing_{i}";
                ring.transform.SetParent(_barRoot, false);
                ring.transform.localScale = new Vector3(0.12f + i * 0.04f, 0.003f, 0.12f + i * 0.04f);
                ring.transform.localPosition = new Vector3(0, 0.02f + i * 0.01f, 0);
                var c = new Color(1f, 0.35f, 0.1f, 0.45f - i * 0.1f);
                ring.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(c);
                Destroy(ring.GetComponent<Collider>());
                _orbitRings.Add(ring.transform);
            }

            _barRoot.gameObject.SetActive(false);
        }

        public void Bind(BossState boss, string bossId)
        {
            _boss = boss;
            _bossId = bossId ?? "earth";

            if (_lastFuryTurns > 0 && boss.FuryCastTurns < 0)
                PlayInterruptBurst();

            _lastFuryTurns = boss.FuryCastTurns;
            var casting = boss.FuryCastTurns > 0;
            _barRoot.gameObject.SetActive(casting);
            if (!casting) return;

            var palette = PaletteForBoss(_bossId);
            var maxTurns = 2f;
            var ratio = Mathf.Clamp01(boss.FuryCastTurns / maxTurns);
            _fill.localScale = new Vector3(0.36f * ratio, 0.032f, 0.038f);
            _fill.localPosition = new Vector3(-0.18f * (1f - ratio), 0, -0.001f);

            _pulse += Time.deltaTime * (boss.FuryCastTurns == 1 ? 7f : 4f);
            var urgent = boss.FuryCastTurns == 1;
            _urgentGlow.gameObject.SetActive(urgent);
            if (urgent)
            {
                var glow = 0.35f + Mathf.Sin(_pulse) * 0.25f;
                _urgentGlow.GetComponent<Renderer>().material.color =
                    new Color(palette.r, palette.g, palette.b, glow);
            }

            var fillColor = Color.Lerp(palette * 1.2f, palette, ratio);
            fillColor.r += Mathf.Sin(_pulse) * 0.12f;
            _fill.GetComponent<Renderer>().material.color = fillColor;

            AnimateOrbitRings(palette, urgent);
        }

        private void AnimateOrbitRings(Color palette, bool urgent)
        {
            for (var i = 0; i < _orbitRings.Count; i++)
            {
                var ring = _orbitRings[i];
                if (ring == null) continue;
                var speed = (urgent ? 120f : 60f) * (i + 1);
                ring.Rotate(Vector3.up, speed * Time.deltaTime, Space.Self);
                var s = 0.12f + i * 0.04f + Mathf.Sin(_pulse + i) * 0.015f;
                ring.localScale = new Vector3(s, 0.003f, s);
                ring.GetComponent<Renderer>().material.color =
                    new Color(palette.r, palette.g, palette.b, 0.35f - i * 0.08f);
            }
        }

        private static Color PaletteForBoss(string bossId) => bossId switch
        {
            "wind" => new Color(0.45f, 0.75f, 1f),
            _ => new Color(0.95f, 0.25f, 0.08f)
        };

        private void PlayInterruptBurst()
        {
            if (_interruptRoutine != null) StopCoroutine(_interruptRoutine);
            _interruptRoutine = StartCoroutine(InterruptBurstRoutine());
        }

        private IEnumerator InterruptBurstRoutine()
        {
            var origin = _barRoot.position;
            var color = _bossId == "wind"
                ? new Color(0.5f, 0.9f, 1f)
                : new Color(1f, 0.85f, 0.2f);

            for (var i = 0; i < 3; i++)
            {
                var shard = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                shard.transform.position = origin;
                shard.transform.localScale = Vector3.one * 0.04f;
                shard.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(color);
                Destroy(shard.GetComponent<Collider>());
                StartCoroutine(AnimateShard(shard, Random.insideUnitSphere * 0.25f));
            }

            var ring = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            ring.transform.position = origin;
            ring.transform.localScale = new Vector3(0.05f, 0.004f, 0.05f);
            ring.GetComponent<Renderer>().material = ProceduralAssets.CreateUnlitMaterial(color);
            Destroy(ring.GetComponent<Collider>());

            for (var t = 0f; t < 0.6f; t += Time.deltaTime)
            {
                var s = Mathf.Lerp(0.05f, 0.35f, t / 0.6f);
                ring.transform.localScale = new Vector3(s, 0.004f, s);
                yield return null;
            }
            Destroy(ring);
            _interruptRoutine = null;
        }

        private static IEnumerator AnimateShard(GameObject shard, Vector3 velocity)
        {
            var life = 0.45f;
            var start = shard.transform.position;
            for (var t = 0f; t < life; t += Time.deltaTime)
            {
                if (shard == null) yield break;
                shard.transform.position = start + velocity * (t / life) + Vector3.up * Mathf.Sin(t * 8f) * 0.03f;
                shard.transform.localScale = Vector3.one * Mathf.Lerp(0.04f, 0.01f, t / life);
                yield return null;
            }
            if (shard != null) Destroy(shard);
        }
    }
}
