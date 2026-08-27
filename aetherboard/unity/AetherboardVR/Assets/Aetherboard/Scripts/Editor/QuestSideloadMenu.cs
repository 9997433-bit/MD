#if UNITY_EDITOR
using System;
using System.Diagnostics;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Aetherboard.Editor
{
    public static class QuestSideloadMenu
    {
        private const string DefaultApkName = "AetherboardVR.apk";

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

            InstallApk(path);
        }

        [MenuItem("Aetherboard/Quest/Install APK to Device...")]
        public static void InstallApkPicker()
        {
            var path = EditorUtility.OpenFilePanel("Select Quest APK", "", "apk");
            if (string.IsNullOrEmpty(path)) return;
            InstallApk(path);
        }

        [MenuItem("Aetherboard/Quest/Open Quest Verification Guide")]
        public static void OpenVerificationGuide()
        {
            var path = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/QUEST_VERIFICATION.md"));
            if (File.Exists(path)) EditorUtility.RevealInFinder(path);
            else Debug.LogWarning("QUEST_VERIFICATION.md not found.");
        }

        private static void InstallApk(string apkPath)
        {
            if (!TryGetAdbPath(out var adb))
            {
                Debug.LogError("Aetherboard: adb not found.");
                return;
            }

            var devices = RunProcess(adb, "devices");
            if (devices == null || !devices.Contains("device"))
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
    }
}
#endif
