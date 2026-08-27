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
        private const string PipelinePath = SettingsDir + "/AetherboardUniversalRP.asset";
        private const string RendererPath = SettingsDir + "/AetherboardForwardRenderer.asset";

        [MenuItem("Aetherboard/Configure URP Pipeline")]
        public static void ConfigureUrpPipeline()
        {
            Directory.CreateDirectory(SettingsDir);

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

            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log(
                "Aetherboard: URP configured.\n" +
                $"  Pipeline: {PipelinePath}\n" +
                $"  Renderer: {RendererPath}\n" +
                "Quest: disable HDR in Player Settings if banding appears.");
        }

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
