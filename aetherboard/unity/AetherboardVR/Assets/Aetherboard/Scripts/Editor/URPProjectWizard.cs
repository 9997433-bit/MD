#if UNITY_EDITOR && AETHERBOARD_URP_INSTALLED
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Aetherboard.Editor
{
    public static class URPProjectWizard
    {
        private const string SettingsDir = "Assets/Aetherboard/Settings";
        private const string ResourcesSettingsDir = "Assets/Aetherboard/Resources/Aetherboard/Settings";
        private const string PipelinePath = SettingsDir + "/AetherboardUniversalRP.asset";
        private const string RendererPath = SettingsDir + "/AetherboardForwardRenderer.asset";
        private const string VolumeProfilePath = ResourcesSettingsDir + "/BattleVolumeProfile.asset";

        [MenuItem("Aetherboard/Configure URP Pipeline")]
        public static void ConfigureUrpPipeline()
        {
            Directory.CreateDirectory(SettingsDir);
            Directory.CreateDirectory(ResourcesSettingsDir);

            var renderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(RendererPath);
            if (renderer == null)
            {
                renderer = ScriptableObject.CreateInstance<UniversalRendererData>();
                renderer.name = "AetherboardForwardRenderer";
                AssetDatabase.CreateAsset(renderer, RendererPath);
            }

            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelinePath);
            if (pipeline == null)
            {
                pipeline = ScriptableObject.CreateInstance<UniversalRenderPipelineAsset>();
                pipeline.name = "AetherboardUniversalRP";
                AssetDatabase.CreateAsset(pipeline, PipelinePath);
            }

            AssignRenderer(pipeline, renderer);
            ApplyQuestFriendlyDefaults(pipeline);
            EnsureBattleVolumeProfile();

            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log(
                "Aetherboard: URP configured.\n" +
                $"  Pipeline: {PipelinePath}\n" +
                $"  Renderer: {RendererPath}\n" +
                $"  Volume: {VolumeProfilePath}\n" +
                "Quest: disable HDR in Player Settings if banding appears.");
        }

        private static void EnsureBattleVolumeProfile()
        {
            var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>(VolumeProfilePath);
            if (profile == null)
            {
                profile = ScriptableObject.CreateInstance<VolumeProfile>();
                profile.name = "BattleVolumeProfile";
                AssetDatabase.CreateAsset(profile, VolumeProfilePath);
            }

            var bloom = profile.TryGet(out Bloom existingBloom) ? existingBloom : profile.Add<Bloom>(true);
            bloom.intensity.Override(0.32f);
            bloom.threshold.Override(0.92f);
            bloom.scatter.Override(0.62f);

            var color = profile.TryGet(out ColorAdjustments existingColor)
                ? existingColor
                : profile.Add<ColorAdjustments>(true);
            color.postExposure.Override(0.08f);
            color.contrast.Override(6f);
            color.saturation.Override(10f);

            var vignette = profile.TryGet(out Vignette existingVignette)
                ? existingVignette
                : profile.Add<Vignette>(true);
            vignette.intensity.Override(0.2f);
            vignette.smoothness.Override(0.38f);

            EditorUtility.SetDirty(profile);

        [MenuItem("Aetherboard/Configure URP Pipeline", true)]
        private static bool ValidateConfigureUrp() => !Application.isPlaying;

        [MenuItem("Aetherboard/Open URP Setup Guide")]
        public static void OpenUrpGuide()
        {
            var path = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/URP_SETUP.md"));
            if (File.Exists(path)) EditorUtility.RevealInFinder(path);
            else Debug.LogWarning("URP_SETUP.md not found.");
        }

        private static void AssignRenderer(UniversalRenderPipelineAsset pipeline, UniversalRendererData renderer)
        {
            var so = new SerializedObject(pipeline);
            var list = so.FindProperty("m_RendererDataList");
            if (list == null) return;

            list.arraySize = 1;
            list.GetArrayElementAtIndex(0).objectReferenceValue = renderer;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void ApplyQuestFriendlyDefaults(UniversalRenderPipelineAsset pipeline)
        {
            pipeline.shadowDistance = 12f;
            pipeline.shadowCascadeCount = 1;
            pipeline.supportsHDR = false;
            pipeline.msaaSampleCount = 4;
            pipeline.renderScale = 1f;
            EditorUtility.SetDirty(pipeline);
        }
    }
}
#else
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Aetherboard.Editor
{
    public static class URPProjectWizard
    {
        [MenuItem("Aetherboard/Configure URP Pipeline")]
        public static void ConfigureUrpPipeline()
        {
            Debug.LogWarning(
                "Aetherboard: URP package not resolved. Reopen project after manifest installs " +
                "com.unity.render-pipelines.universal, then retry.");
        }

        [MenuItem("Aetherboard/Open URP Setup Guide")]
        public static void OpenUrpGuide()
        {
            var path = System.IO.Path.GetFullPath(
                System.IO.Path.Combine(Application.dataPath, "../../docs/URP_SETUP.md"));
            if (System.IO.File.Exists(path)) EditorUtility.RevealInFinder(path);
        }
    }
}
#endif
#endif
