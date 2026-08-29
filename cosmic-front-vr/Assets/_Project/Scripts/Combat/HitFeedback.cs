using UnityEngine;

namespace CosmicFront.Combat
{
    /// <summary>
    /// Temporary hit-point flash (primitive sphere). No particle assets required.
    /// </summary>
    public static class HitFeedback
    {
        private const float DefaultDuration = 0.15f;
        private const float DefaultScale = 0.35f;

        public static void Spawn(Vector3 position, float duration = DefaultDuration)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = "HitFeedback";
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
                renderer.material.color = new Color(1f, 0.75f, 0.15f, 1f);
            }

            Object.Destroy(go, duration);
        }
    }
}
