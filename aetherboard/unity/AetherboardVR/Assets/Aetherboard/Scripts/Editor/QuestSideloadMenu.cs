#if UNITY_EDITOR
using System;
using System.Diagnostics;
using System.IO;
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    public static class QuestSideloadMenu
    {
        private const string DefaultApkName = "AetherboardVR.apk";
        private const string UnityActivity = "com.unity3d.player.UnityPlayerActivity";

        [MenuItem("Aetherboard/Quest/Check Connected Device (ADB)")]
        public static void CheckDevice()
        {
            if (!TryGetAdbPath(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found. Install Android SDK / set ANDROID_HOME.");
                return;
            }

            var output = RunProcess(adb, "devices -l");
            if (string.IsNullOrWhiteSpace(output) || output.Trim() == "List of devices attached")
                Debug.LogWarning("Aetherboard: No Android device detected. Enable Quest developer mode + USB debugging.");
            else
                Debug.Log($"Aetherboard: ADB devices:\n{output}");
        }

        [MenuItem("Aetherboard/Quest/Install Last Built APK")]
        public static void InstallLastBuiltApk()
        {
            var path = Path.GetFullPath(Path.Combine(Application.dataPath, $"../../build/{DefaultApkName}"));
            if (!File.Exists(path))
            {
                Debug.LogError($"Aetherboard: APK not found at {path}. Run Build Quest APK first.");
                return;
            }

            InstallApkPublic(path);
        }

        [MenuItem("Aetherboard/Quest/Install APK to Device...")]
        public static void InstallApkPicker()
        {
            var path = EditorUtility.OpenFilePanel("Select Quest APK", "", "apk");
            if (string.IsNullOrEmpty(path)) return;
            InstallApkPublic(path);
        }

        [MenuItem("Aetherboard/Quest/Launch App on Device")]
        public static void LaunchAppMenu() => LaunchAppPublic();

        [MenuItem("Aetherboard/Quest/Pull Verification Report")]
        public static void PullReportMenu() => PullVerificationReportPublic();

        [MenuItem("Aetherboard/Quest/Open Quest Verification Guide")]
        public static void OpenVerificationGuide()
        {
            var path = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/QUEST_VERIFICATION.md"));
            if (File.Exists(path)) EditorUtility.RevealInFinder(path);
            else Debug.LogWarning("QUEST_VERIFICATION.md not found.");
        }

        [MenuItem("Aetherboard/Quest/Tail Aetherboard Logs (ADB)")]
        public static void TailAetherboardLogs()
        {
            if (!TryGetAdbPath(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found.");
                return;
            }

            if (!HasAuthorizedDevice(adb))
            {
                Debug.LogError("Aetherboard: No authorized device. Connect Quest and run Check Connected Device.");
                return;
            }

            Debug.Log(
                "Aetherboard: Tailing logcat (Unity | Aetherboard). Stop with Ctrl+C in terminal.\n" +
                $"Command: {adb} logcat -s Unity | grep Aetherboard");
            RunProcessStreaming(adb, "logcat -s Unity");
        }

        [MenuItem("Aetherboard/Quest/Clear Logcat Buffer")]
        public static void ClearLogcat() => ClearLogcatPublic();

        public static bool TryGetAdbPathPublic(out string adbPath) => TryGetAdbPath(out adbPath);

        public static void InstallApkPublic(string apkPath)
        {
            if (!TryGetAdbPath(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found.");
                return;
            }

            if (!HasAuthorizedDevice(adb))
            {
                Debug.LogError("Aetherboard: No authorized device. Run Check Connected Device first.");
                return;
            }

            Debug.Log($"Aetherboard: Installing {apkPath} ...");
            var result = RunProcess(adb, $"install -r \"{apkPath}\"");
            if (result != null && result.Contains("Success", StringComparison.OrdinalIgnoreCase))
                Debug.Log("Aetherboard: APK installed. Launch from Quest Library → Unknown Sources.");
            else
                Debug.LogError($"Aetherboard: adb install failed:\n{result}");
        }

        public static void LaunchAppPublic()
        {
            if (!TryGetAdbPath(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found.");
                return;
            }

            if (!HasAuthorizedDevice(adb))
            {
                Debug.LogError("Aetherboard: No authorized device.");
                return;
            }

            var component = $"{QuestVerificationReport.PackageId}/{UnityActivity}";
            var result = RunProcess(adb, $"shell am start -n {component}");
            Debug.Log($"Aetherboard: Launched {component}\n{result}");
        }

        public static void ClearLogcatPublic()
        {
            if (!TryGetAdbPath(out var adb)) return;
            RunProcess(adb, "logcat -c");
            Debug.Log("Aetherboard: logcat buffer cleared.");
        }

        public static void PullVerificationReportPublic()
        {
            if (!TryGetAdbPath(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found.");
                return;
            }

            var localDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../build/quest_reports"));
            Directory.CreateDirectory(localDir);
            var localPath = Path.Combine(localDir, QuestVerificationReport.ReportFileName);

            var remotePath = QuestVerificationReport.PublicReportPath;
            var pullResult = RunProcess(adb, $"pull \"{remotePath}\" \"{localPath}\"");
            if (File.Exists(localPath))
            {
                var text = File.ReadAllText(localPath);
                var failures = QuestVerificationReport.CountFailures(text);
                Debug.Log(
                    $"Aetherboard: Pulled verification report → {localPath}\n" +
                    $"Automated FAIL count: {failures}\n{text}");
                return;
            }

            Debug.LogWarning(
                $"Aetherboard: Report not found at {remotePath}. Launch app and wait for diagnostics.\n{pullResult}");
        }

        public static void TailRecentLogsPublic(string adb, int lineCount)
        {
            var output = RunProcess(adb, "logcat -d -s Unity");
            if (string.IsNullOrEmpty(output))
            {
                Debug.LogWarning("Aetherboard: No Unity logcat output.");
                return;
            }

            var lines = output.Split('\n');
            var matched = 0;
            var sb = new System.Text.StringBuilder();
            sb.AppendLine("Aetherboard: Recent Quest logcat (filtered):");
            for (var i = Math.Max(0, lines.Length - lineCount); i < lines.Length; i++)
            {
                if (!lines[i].Contains("Aetherboard", StringComparison.Ordinal)) continue;
                sb.AppendLine(lines[i]);
                matched++;
            }

            if (matched == 0)
                sb.AppendLine("  (no Aetherboard lines in recent logcat — launch app first)");
            Debug.Log(sb.ToString());
        }

        private static bool HasAuthorizedDevice(string adb)
        {
            var devices = RunProcess(adb, "devices");
            return devices != null && devices.Contains("device");
        }

        private static bool TryGetAdbPath(out string adbPath)
        {
            var sdk = EditorPrefs.GetString("AndroidSdkRoot");
            if (string.IsNullOrEmpty(sdk))
                sdk = Environment.GetEnvironmentVariable("ANDROID_HOME")
                      ?? Environment.GetEnvironmentVariable("ANDROID_SDK_ROOT");

            if (!string.IsNullOrEmpty(sdk))
            {
                adbPath = Path.Combine(sdk, "platform-tools", GetAdbExecutableName());
                if (File.Exists(adbPath)) return true;
            }

            adbPath = GetAdbExecutableName();
            return File.Exists(adbPath) || RunProcess("which", GetAdbExecutableName()) != null;
        }

        private static string GetAdbExecutableName() =>
            Application.platform == RuntimePlatform.WindowsEditor ? "adb.exe" : "adb";

        private static string RunProcess(string fileName, string arguments)
        {
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = fileName,
                    Arguments = arguments,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                using var process = Process.Start(psi);
                if (process == null) return null;
                var stdout = process.StandardOutput.ReadToEnd();
                var stderr = process.StandardError.ReadToEnd();
                process.WaitForExit(15000);
                return string.IsNullOrWhiteSpace(stdout) ? stderr : stdout + stderr;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Aetherboard: Process failed ({fileName}): {ex.Message}");
                return null;
            }
        }

        private static void RunProcessStreaming(string fileName, string arguments)
        {
            try
            {
                var psi = new ProcessStartInfo
                {
                    FileName = fileName,
                    Arguments = arguments,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                var process = Process.Start(psi);
                if (process == null) return;

                process.OutputDataReceived += (_, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data) && e.Data.Contains("Aetherboard"))
                        Debug.Log($"[Quest logcat] {e.Data}");
                };
                process.BeginOutputReadLine();
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Aetherboard: Streaming logcat failed: {ex.Message}");
            }
        }
    }
}
#endif
