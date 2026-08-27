using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Battle table lighting — trilight ambient + key/fill/rim for VR readability.
    /// </summary>
    public static class BattleLightingController
    {
        private static bool _initialized;

        public static void SetupBattleLighting(Vector3? tableCenter = null)
        {
            if (_initialized) return;
            _initialized = true;

            ApplyAmbient();
            EnsureLight("Key Light", LightType.Directional,
                new Color(1f, 0.95f, 0.88f), 1.05f,
                Quaternion.Euler(52f, -35f, 0f), LightShadows.Soft);
            EnsureLight("Fill Light", LightType.Directional,
                new Color(0.55f, 0.65f, 0.85f), 0.35f,
                Quaternion.Euler(25f, 120f, 0f), LightShadows.None);
            EnsureLight("Rim Light", LightType.Directional,
                new Color(0.75f, 0.55f, 0.35f), 0.25f,
                Quaternion.Euler(10f, 200f, 0f), LightShadows.None);

            if (tableCenter.HasValue)
            {
                EnsureLight("Table Accent", LightType.Point,
                    new Color(0.45f, 0.6f, 0.9f), 0.5f,
                    tableCenter.Value + new Vector3(0, 0.6f, 0.2f),
                    LightShadows.None, 1.8f);
            }
        }

        public static void ApplyQuestProfile()
        {
            RenderSettings.ambientIntensity = 0.85f;
            foreach (var light in Object.FindObjectsOfType<Light>())
            {
                light.shadows = LightShadows.None;
                if (light.type == LightType.Directional)
                    light.intensity *= 0.9f;
            }
        }

        private static void ApplyAmbient()
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.22f, 0.26f, 0.34f);
            RenderSettings.ambientEquatorColor = new Color(0.16f, 0.18f, 0.22f);
            RenderSettings.ambientGroundColor = new Color(0.08f, 0.09f, 0.11f);
            RenderSettings.ambientIntensity = 1f;
        }

        private static void EnsureLight(
            string name,
            LightType type,
            Color color,
            float intensity,
            Quaternion rotation,
            LightShadows shadows)
        {
            var existing = GameObject.Find(name);
            if (existing != null) return;

            var go = new GameObject(name);
            var light = go.AddComponent<Light>();
            light.type = type;
            light.color = color;
            light.intensity = intensity;
            light.shadows = shadows;
            go.transform.rotation = rotation;
        }

        private static void EnsureLight(
            string name,
            LightType type,
            Color color,
            float intensity,
            Vector3 position,
            LightShadows shadows,
            float range)
        {
            var existing = GameObject.Find(name);
            if (existing != null) return;

            var go = new GameObject(name);
            go.transform.position = position;
            var light = go.AddComponent<Light>();
            light.type = type;
            light.color = color;
            light.intensity = intensity;
            light.range = range;
            light.shadows = shadows;
        }
    }
}
