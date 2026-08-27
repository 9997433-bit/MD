#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;

namespace Aetherboard.Editor
{
    /// <summary>
    /// Chains recommended Editor setup steps for new clones / first open.
    /// </summary>
    public static class AetherboardFirstTimeSetup
    {
        private const string ScenePath = "Assets/Aetherboard/Scenes/BattleTable.unity";

        [MenuItem("Aetherboard/First Time Setup (Recommended)")]
        public static void RunFirstTimeSetup()
        {
            if (Application.isPlaying)
            {
                Debug.LogWarning("Aetherboard: Exit Play mode before running first-time setup.");
                return;
            }

            Debug.Log("Aetherboard: First-time setup started...");

            OpenXRProjectWizard.ConfigureQuestBuild();
            URPProjectWizard.ConfigureUrpPipeline();
            BattlePrefabInstaller.InstallBattleTablePrefabs();
            XROriginPrefabInstaller.Install();

            if (!File.Exists(ScenePath))
                BattleSceneSetupMenu.CreateBattleScene();
            else
                Debug.Log($"Aetherboard: Scene already exists at {ScenePath} — skipped creation.");

            QuestReadyWizard.RunReadinessCheck();

            Debug.Log(
                "Aetherboard: First-time setup complete.\n" +
                "  Next: Press Play to test desktop mode.\n" +
                "  Quest: Build Quest APK to build/ → Quest → Install Last Built APK.");
        }

        [MenuItem("Aetherboard/First Time Setup (Recommended)", true)]
        private static bool ValidateFirstTimeSetup() => !Application.isPlaying;
    }
}
#endif
