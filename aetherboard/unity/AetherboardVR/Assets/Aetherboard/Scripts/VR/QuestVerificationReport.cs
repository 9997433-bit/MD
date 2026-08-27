using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Builds Quest sideload verification reports for logcat and on-device export.
    /// </summary>
    public static class QuestVerificationReport
    {
        public const string PackageId = "com.aetherboard.vr";
        public const string ReportFileName = "quest_verification.txt";
        public const string PublicReportPath = "/sdcard/Download/quest_verification.txt";

        public static string BuildReport(bool includeManualChecklist = true)
        {
            var sb = new StringBuilder();
            sb.AppendLine("[Aetherboard Quest] Verification report");
            sb.AppendLine($"  Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC");
            sb.AppendLine($"  Version: {Application.version}");
            sb.AppendLine($"  Device: {SystemInfo.deviceModel} / {SystemInfo.operatingSystem}");
            sb.AppendLine($"  GPU: {SystemInfo.graphicsDeviceName}");
            sb.AppendLine($"  Target FPS: {Application.targetFrameRate}");
            sb.AppendLine($"  XR: {UnityEngine.XR.XRSettings.enabled} ({UnityEngine.XR.XRSettings.loadedDeviceName})");
            sb.AppendLine($"  Prefabs: {(BattlePrefabLibrary.HasPrefabs ? "Resources" : "Procedural")}");
            sb.AppendLine($"  External art: {(BattleArtCatalog.HasExternalArt ? "yes" : "no")}");
            sb.AppendLine(BattleArtCatalog.BuildInventoryReport().Replace("\n", "\n  "));
            sb.AppendLine($"  LAN IP: {TryGetLanIp()}");
            sb.AppendLine($"  Saved Host: {BattleNetPrefs.LoadHost()}");
            sb.AppendLine("  VR Panel: 桌台右侧联机面板 | 键盘输入=Quest IP");
            AppendAutomatedChecks(sb);

            if (includeManualChecklist)
                AppendManualChecklist(sb);

            return sb.ToString();
        }

        public static int CountFailures(string report)
        {
            if (string.IsNullOrEmpty(report)) return 0;
            var count = 0;
            var index = 0;
            while ((index = report.IndexOf("[FAIL]", index, StringComparison.Ordinal)) >= 0)
            {
                count++;
                index += 6;
            }
            return count;
        }

        public static string WriteReportFiles()
        {
            var report = BuildReport();
            var primaryPath = Path.Combine(Application.persistentDataPath, ReportFileName);
            File.WriteAllText(primaryPath, report);

#if UNITY_ANDROID && !UNITY_EDITOR
            try
            {
                File.WriteAllText(PublicReportPath, report);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Aetherboard: Could not write public report: {ex.Message}");
            }
#endif

            return primaryPath;
        }

        private static void AppendAutomatedChecks(StringBuilder sb)
        {
            sb.AppendLine("[Aetherboard Quest] Automated checks:");
            LogCheck(sb, "BattleDirector", UnityEngine.Object.FindObjectOfType<BattleDirector>() != null);
            LogCheck(sb, "BattleTableView", UnityEngine.Object.FindObjectOfType<BattleTableView>() != null);
            LogCheck(sb, "SkillRing", UnityEngine.Object.FindObjectOfType<SkillRingController>() != null);
            LogCheck(sb, "BattleNetSession", UnityEngine.Object.FindObjectOfType<BattleNetSession>() != null);
            LogCheck(sb, "ResultOverlay", UnityEngine.Object.FindObjectOfType<BattleResultOverlay>() != null);
            LogCheck(sb, "BossSelectPanel", UnityEngine.Object.FindObjectOfType<BattleBossSelectPanel>() != null);

            var pieces = UnityEngine.Object.FindObjectsOfType<PieceToken>();
            LogCheck(sb, "PieceTokens>=4", pieces != null && pieces.Length >= 4);

#if UNITY_ANDROID && !UNITY_EDITOR
            LogCheck(sb, "XR enabled", UnityEngine.XR.XRSettings.enabled);
#else
            sb.AppendLine("  [SKIP] XR enabled (desktop/editor)");
#endif
        }

        private static void AppendManualChecklist(StringBuilder sb)
        {
            sb.AppendLine("[Aetherboard Quest] Manual checklist (operator marks on device):");
            sb.AppendLine("  [ ] 1 Launch — 7x7 table visible");
            sb.AppendLine("  [ ] 2 Frame rate — stable 72fps");
            sb.AppendLine("  [ ] 3 Grab — piece follows controller");
            sb.AppendLine("  [ ] 4 Move — legal placement advances phase");
            sb.AppendLine("  [ ] 5 Skill ring — trigger opens chips");
            sb.AppendLine("  [ ] 6 Cast bar VFX — boss telegraph visible");
            sb.AppendLine("  [ ] 7 Co-op — P1/P2 permissions");
            sb.AppendLine("  [ ] 8 Online WS — PC host sync");
            sb.AppendLine("  [ ] 9 Online NGO — NetcodeNative 7777");
            sb.AppendLine("  [ ] 10 Audio — phase/damage SFX");
        }

        private static void LogCheck(StringBuilder sb, string label, bool pass)
        {
            sb.AppendLine($"  [{(pass ? "PASS" : "FAIL")}] {label}");
        }

        private static string TryGetLanIp()
        {
            try
            {
                foreach (var address in Dns.GetHostEntry(Dns.GetHostName()).AddressList)
                {
                    if (address.AddressFamily == AddressFamily.InterNetwork && !IPAddress.IsLoopback(address))
                        return address.ToString();
                }
            }
            catch
            {
                // ignore on restricted Android profiles
            }

            return "unknown";
        }
    }
}
