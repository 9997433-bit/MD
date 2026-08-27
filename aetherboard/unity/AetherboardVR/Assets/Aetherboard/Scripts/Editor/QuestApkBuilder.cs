#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Aetherboard.Editor
{
    public static class QuestApkBuilder
    {
        private const string DefaultApkName = "AetherboardVR.apk";

        [MenuItem("Aetherboard/Build Quest APK to build/")]
        public static void BuildQuestApkToBuildFolder()
        {
            OpenXRProjectWizard.ConfigureQuestBuild();
            var outputPath = Path.GetFullPath(Path.Combine(Application.dataPath, $"../../build/{DefaultApkName}"));
            Directory.CreateDirectory(Path.GetDirectoryName(outputPath) ?? ".");
            BuildApkAtPath(outputPath);
        }

        [MenuItem("Aetherboard/Build Quest APK...")]
        public static void BuildQuestApk()
        {
            OpenXRProjectWizard.ConfigureQuestBuild();

            var defaultDir = Path.Combine(Application.dataPath, "../../build");
            Directory.CreateDirectory(defaultDir);
            var defaultPath = Path.GetFullPath(Path.Combine(defaultDir, DefaultApkName));

            var outputPath = EditorUtility.SaveFilePanel(
                "Build Quest APK",
                Path.GetDirectoryName(defaultPath),
                Path.GetFileName(defaultPath),
                "apk");

            if (string.IsNullOrEmpty(outputPath)) return;
            BuildApkAtPath(outputPath);
        }

        private static void BuildApkAtPath(string outputPath)
        {
            var scenes = EditorBuildSettings.scenes;
            if (scenes == null || scenes.Length == 0)
            {
                Debug.LogError("Aetherboard: No scenes in Build Settings. Run Create Battle Scene File first.");
                return;
            }

            var options = new BuildPlayerOptions
            {
                scenes = GetEnabledScenePaths(scenes),
                locationPathName = outputPath,
                target = BuildTarget.Android,
                options = BuildOptions.None
            };

            Debug.Log($"Aetherboard: Building Quest APK → {outputPath}");
            var report = BuildPipeline.BuildPlayer(options);
            LogBuildResult(report);
        }

        private static string[] GetEnabledScenePaths(EditorBuildSettingsScene[] scenes)
        {
            var paths = new System.Collections.Generic.List<string>();
            foreach (var scene in scenes)
            {
                if (scene.enabled) paths.Add(scene.path);
            }
            return paths.ToArray();
        }

        private static void LogBuildResult(BuildReport report)
        {
            if (report.summary.result == BuildResult.Succeeded)
            {
                Debug.Log(
                    $"Aetherboard: APK build succeeded ({report.summary.totalSize} bytes) → {report.summary.outputPath}");
                return;
            }

            Debug.LogError($"Aetherboard: APK build failed — {report.summary.result}");
        }
    }
}
#endif
