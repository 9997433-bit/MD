using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Particle bursts on mechanic resolve (no external assets).
    /// </summary>
    public class BattleParticleVFX : MonoBehaviour
    {
        private BattleDirector _director;
        private BattleTableView _table;

        public void Bind(BattleDirector director, BattleTableView table)
        {
            _director = director;
            _table = table;
            _director.OnPhaseChanged.AddListener(OnPhaseChanged);
        }

        private void OnDestroy()
        {
            if (_director != null)
                _director.OnPhaseChanged.RemoveListener(OnPhaseChanged);
        }

        private void OnPhaseChanged(BattlePhase phase)
        {
            if (phase != BattlePhase.Move) return;
            var telegraph = _director.State.Boss.Telegraph;
            if (telegraph == TelegraphKind.None) return;

            foreach (var pos in _director.State.PreviewCells)
            {
                var color = telegraph switch
                {
                    TelegraphKind.Slam or TelegraphKind.EarthenFury => new Color(1f, 0.2f, 0.1f),
                    TelegraphKind.Earthquake => new Color(0.6f, 0.4f, 0.1f),
                    TelegraphKind.Shrink => new Color(0.8f, 0.1f, 0.1f),
                    TelegraphKind.Gale => new Color(0.5f, 0.8f, 1f),
                    TelegraphKind.Spread => new Color(1f, 0.6f, 0.2f),
                    TelegraphKind.Stack => new Color(0.3f, 0.9f, 0.4f),
                    TelegraphKind.Cyclone => new Color(0.7f, 0.5f, 1f),
                    TelegraphKind.IceLance => new Color(0.5f, 0.85f, 1f),
                    TelegraphKind.FrozenGround => new Color(0.35f, 0.7f, 1f),
                    TelegraphKind.IceRing => new Color(0.6f, 0.95f, 1f),
                    TelegraphKind.Blizzard => new Color(0.75f, 0.9f, 1f),
                    _ => Color.white
                };
                Burst(_table.GridToWorld(pos.X, pos.Y), color);
            }
        }

        private static void Burst(Vector3 worldPos, Color color)
        {
            var go = new GameObject("ParticleBurst");
            go.transform.position = worldPos + Vector3.up * 0.05f;
            var ps = go.AddComponent<ParticleSystem>();
            var main = ps.main;
            main.duration = 0.4f;
            main.startLifetime = 0.35f;
            main.startSpeed = 0.8f;
            main.startSize = 0.04f;
            main.startColor = color;
            main.loop = false;
            main.maxParticles = 24;
            var emission = ps.emission;
            emission.rateOverTime = 0;
            emission.SetBursts(new[] { new ParticleSystem.Burst(0f, 16) });
            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.04f;
            ps.Play();
            Object.Destroy(go, 1.5f);
        }
    }
}
