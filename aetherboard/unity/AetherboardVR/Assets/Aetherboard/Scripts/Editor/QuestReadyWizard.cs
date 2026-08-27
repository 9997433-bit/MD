#if UNITY_EDITOR
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    /// <summary>
    /// Pre-build readiness checks before Quest APK sideload.
    /// </summary>
    public static class QuestReadyWizard
    {
        private const string ScenePath = "Assets/Aetherboard/Scenes/BattleTable.unity";
        private const string GridCellPath = "Assets/Aetherboard/Resources/Aetherboard/GridCell.prefab";
        private const string XrOriginPath = "Assets/Aetherboard/Resources/Aetherboard/XROriginRig.prefab";
        private const string DefaultApkPath = "build/AetherboardVR.apk";

        [MenuItem("Aetherboard/Quest/Run Pre-Build Readiness Check")]
        public static void RunReadinessCheck()
        {
            var sb = new StringBuilder();
            sb.AppendLine("Aetherboard Quest readiness report");
            sb.AppendLine("==================================");

            var pass = 0;
            var warn = 0;
            var fail = 0;

            Check(BuildSceneRegistered(), "Build scene registered", ref pass, ref warn, ref fail, sb);
            Check(File.Exists(GridCellPath), "Battle table prefabs installed", ref pass, ref warn, ref fail, sb,
                warnIfMissing: true,
                hint: "Run Aetherboard → Install Battle Table Prefabs");
            Check(File.Exists(XrOriginPath), "XR Origin prefab installed", ref pass, ref warn, ref fail, sb,
                warnIfMissing: true,
                hint: "Run Aetherboard → Install XR Origin Prefab");
            Check(IsAndroidTarget(), "Active build target is Android", ref pass, ref warn, ref fail, sb,
                hint: "Run Aetherboard → Configure Quest (Android) Build Settings");
            Check(IsQuestPackageId(), "Package ID com.aetherboard.vr", ref pass, ref warn, ref fail, sb);
            Check(File.Exists(GetApkPath()), "Last APK exists in build/", ref pass, ref warn, ref fail, sb,
                warnIfMissing: true,
                hint: "Run Aetherboard → Build Quest APK to build/");

            sb.AppendLine();
            sb.AppendLine("Art inventory:");
            sb.AppendLine(BattleArtCatalog.BuildInventoryReport());

            sb.AppendLine();
            sb.AppendLine($"Summary: {pass} pass, {warn} warn, {fail} fail");
            if (fail == 0)
                sb.AppendLine("Ready to build/install Quest APK.");
            else
                sb.AppendLine("Fix FAIL items before sideloading.");

            Debug.Log(sb.ToString());
        }

        [MenuItem("Aetherboard/Quest/Quest Ready — Install + Launch + Pull Report")]
        public static void RunSmokeTest()
        {
            RunReadinessCheck();

            if (!QuestSideloadMenu.TryGetAdbPathPublic(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found.");
                return;
            }

            var apkPath = GetApkPath();
            if (!File.Exists(apkPath))
            {
                Debug.LogError($"Aetherboard: APK missing at {apkPath}. Build Quest APK first.");
                return;
            }

            QuestSideloadMenu.InstallApkPublic(apkPath);
            QuestSideloadMenu.ClearLogcatPublic();
            QuestSideloadMenu.LaunchAppPublic();
            Debug.Log("Aetherboard: Waiting 12s for Quest boot + diagnostics...");
            System.Threading.Thread.Sleep(12000);
            QuestSideloadMenu.PullVerificationReportPublic();
            QuestSideloadMenu.TailRecentLogsPublic(adb, 80);
        }

        private static void Check(
            bool ok,
            string label,
            ref int pass,
            ref int warn,
            ref int fail,
            StringBuilder sb,
            bool warnIfMissing = false,
            string hint = null)
        {
            if (ok)
            {
                pass++;
                sb.AppendLine($"  [PASS] {label}");
                return;
            }

            if (warnIfMissing)
            {
                warn++;
                sb.AppendLine($"  [WARN] {label}");
            }
            else
            {
                fail++;
                sb.AppendLine($"  [FAIL] {label}");
            }

            if (!string.IsNullOrEmpty(hint))
                sb.AppendLine($"         → {hint}");
        }

        private static bool BuildSceneRegistered()
        {
            foreach (var scene in EditorBuildSettings.scenes)
            {
                if (scene.enabled && scene.path == ScenePath) return true;
            }
            return false;
        }

        private static bool IsAndroidTarget() =>
            EditorUserBuildSettings.activeBuildTarget == BuildTarget.Android;

        private static bool IsQuestPackageId() =>
            PlayerSettings.GetApplicationIdentifier(BuildTargetGroup.Android) == QuestVerificationReport.PackageId;

        private static string GetApkPath() =>
            Path.GetFullPath(Path.Combine(Application.dataPath, $"../../{DefaultApkPath}"));
    }
}
#endif
