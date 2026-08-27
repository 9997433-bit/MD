#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    public static class OpenXRProjectWizard
    {
        [MenuItem("Aetherboard/Configure Quest (Android) Build Settings")]
        public static void ConfigureQuestBuild()
        {
            PlayerSettings.companyName = "Aetherboard";
            PlayerSettings.productName = "Aetherboard VR";
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, QuestVerificationReport.PackageId);
            PlayerSettings.bundleVersion = ReadProjectVersion();
            EditorUserBuildSettings.SwitchActiveBuildTarget(
                BuildTargetGroup.Android, BuildTarget.Android);

            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
            PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevel32;
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.colorSpace = ColorSpace.Linear;
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.virtualRealitySupported = false;

            EditorUserBuildSettings.androidBuildSubtarget = MobileTextureSubtarget.ASTC;
            PlayerSettings.Android.bundleVersionCode = 2;
            PlayerSettings.Android.forceInternetPermission = true;

            EnsureBattleSceneInBuildSettings();
            Debug.Log(
                $"Aetherboard: Android/ARM64/IL2CPP configured ({QuestVerificationReport.PackageId}, v{ReadProjectVersion()}). " +
                "Next: Enable OpenXR in XR Plug-in Management and add Quest interaction profiles.");
        }

        private static string ReadProjectVersion()
        {
            var path = System.IO.Path.GetFullPath(
                System.IO.Path.Combine(Application.dataPath, "../../VERSION"));
            if (!System.IO.File.Exists(path)) return "0.2.0-vr";
            return System.IO.File.ReadAllText(path).Trim();
        }

        [MenuItem("Aetherboard/Configure PCVR (Standalone) Build Settings")]
        public static void ConfigurePcvrBuild()
        {
            EditorUserBuildSettings.SwitchActiveBuildTarget(
                BuildTargetGroup.Standalone, BuildTarget.StandaloneWindows64);
            PlayerSettings.colorSpace = ColorSpace.Linear;
            EnsureBattleSceneInBuildSettings();
            Debug.Log("Aetherboard: PCVR Windows x64 configured. Enable OpenXR + SteamVR or Oculus PC profile.");
        }

        private static void EnsureBattleSceneInBuildSettings()
        {
            const string scenePath = "Assets/Aetherboard/Scenes/BattleTable.unity";
            var scenes = EditorBuildSettings.scenes;
            foreach (var s in scenes)
                if (s.path == scenePath) return;
            var list = new System.Collections.Generic.List<EditorBuildSettingsScene>(scenes)
            {
                new EditorBuildSettingsScene(scenePath, true)
            };
            EditorBuildSettings.scenes = list.ToArray();
        }
    }
}
#endif
