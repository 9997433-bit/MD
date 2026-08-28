using UnityEngine;

namespace CosmicFront.Combat
{
    /// <summary>
    /// Short bright flash at the weapon fire origin.
    /// </summary>
    public static class MuzzleFlash
    {
        private const float DefaultDuration = 0.08f;
        private const float DefaultScale = 0.2f;
        private const float ForwardOffset = 0.15f;

        public static void Play(Transform origin, float duration = DefaultDuration)
        {
            if (origin == null)
            {
                return;
            }

            Play(origin.position + origin.forward * ForwardOffset, duration);
        }

        public static void Play(Vector3 position, float duration = DefaultDuration)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = "MuzzleFlash";
            go.transform.position = position;
            go.transform.localScale = Vector3.one * DefaultScale;

            var col = go.GetComponent<Collider>();
            if (col != null)
            {
                Object.Destroy(col);
            }

            var renderer = go.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.color = new Color(1f, 0.95f, 0.7f, 1f);
            }

            var light = go.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = 4f;
            light.intensity = 2.5f;
            light.color = new Color(1f, 0.9f, 0.55f);

            Object.Destroy(go, duration);
        }
    }
}
