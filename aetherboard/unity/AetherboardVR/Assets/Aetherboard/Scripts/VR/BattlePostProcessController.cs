using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Optional URP global post-processing for battle table readability (Bloom / color / vignette).
    /// No-op when Built-in pipeline or URP package is unavailable.
    /// </summary>
    public static class BattlePostProcessController
    {
        private const string VolumeObjectName = "Battle Post Process";
        private const string ProfileResourcePath = "Aetherboard/Settings/BattleVolumeProfile";

        private static bool _initialized;

        public static void SetupBattlePostProcess()
        {
#if AETHERBOARD_URP_INSTALLED
            if (_initialized) return;
            _initialized = true;

            if (GameObject.Find(VolumeObjectName) != null) return;

            var profile = Resources.Load<UnityEngine.Rendering.VolumeProfile>(ProfileResourcePath)
                          ?? CreateRuntimeProfile();
            if (profile == null) return;

            var go = new GameObject(VolumeObjectName);
            var volume = go.AddComponent<UnityEngine.Rendering.Volume>();
            volume.isGlobal = true;
            volume.priority = 10f;
            volume.profile = profile;
#else
            _ = _initialized;
#endif
        }

        public static void ApplyQuestProfile()
        {
#if AETHERBOARD_URP_INSTALLED
            var volume = GameObject.Find(VolumeObjectName)?.GetComponent<UnityEngine.Rendering.Volume>();
            if (volume?.profile == null) return;

            if (volume.profile.TryGet(out UnityEngine.Rendering.Universal.Bloom bloom))
            {
                bloom.intensity.Override(0.12f);
                bloom.threshold.Override(1.15f);
            }

            if (volume.profile.TryGet(out UnityEngine.Rendering.Universal.Vignette vignette))
                vignette.intensity.Override(0.14f);
#endif
        }

#if AETHERBOARD_URP_INSTALLED
        private static UnityEngine.Rendering.VolumeProfile CreateRuntimeProfile()
        {
            var profile = ScriptableObject.CreateInstance<UnityEngine.Rendering.VolumeProfile>();
            profile.name = "BattleVolumeProfile (Runtime)";

            var bloom = profile.Add<UnityEngine.Rendering.Universal.Bloom>(true);
            bloom.intensity.Override(0.32f);
            bloom.threshold.Override(0.92f);
            bloom.scatter.Override(0.62f);

            var color = profile.Add<UnityEngine.Rendering.Universal.ColorAdjustments>(true);
            color.postExposure.Override(0.08f);
            color.contrast.Override(6f);
            color.saturation.Override(10f);

            var vignette = profile.Add<UnityEngine.Rendering.Universal.Vignette>(true);
            vignette.intensity.Override(0.2f);
            vignette.smoothness.Override(0.38f);

            return profile;
        }
#endif
    }
}
