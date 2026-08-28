#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace CosmicFront.Editor
{
    public static class DedicatedServerBuildMenu
    {
        private const string ServerScene = "Assets/_Project/Scenes/Hangar.unity";

        [MenuItem("Cosmic Front/Build/Dedicated Server (Windows Headless)")]
        public static void BuildDedicatedServer()
        {
            var options = new BuildPlayerOptions
            {
                scenes = new[] { ServerScene },
                locationPathName = "Builds/Server/CosmicFrontServer.exe",
                target = BuildTarget.StandaloneWindows64,
                subtarget = (int)StandaloneBuildSubtarget.Server,
                options = BuildOptions.EnableHeadlessMode | BuildOptions.Development
            };

            var report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result == BuildResult.Succeeded)
            {
                Debug.Log($"Dedicated Server build OK: {options.locationPathName}");
                Debug.Log("Run: CosmicFrontServer.exe -batchmode -nographics -cosmicServer");
            }
            else
            {
                Debug.LogError($"Dedicated Server build failed: {report.summary.result}");
            }
        }
    }
}
#endif
