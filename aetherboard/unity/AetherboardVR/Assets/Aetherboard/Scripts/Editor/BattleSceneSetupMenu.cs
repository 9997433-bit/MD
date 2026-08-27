#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    public static class BattleSceneSetupMenu
    {
        private const string ScenePath = "Assets/Aetherboard/Scenes/BattleTable.unity";

        [MenuItem("Aetherboard/Create Battle Scene File")]
        public static void CreateBattleScene()
        {
            System.IO.Directory.CreateDirectory("Assets/Aetherboard/Scenes");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            var bootstrap = new GameObject("AetherboardBootstrap");
            bootstrap.AddComponent<RuntimeSceneBootstrap>();

            EditorSceneManager.SaveScene(scene, ScenePath);
            var scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            EditorBuildSettings.scenes = scenes;
            Debug.Log($"Aetherboard: Saved {ScenePath} and registered in Build Settings.");
        }

        [MenuItem("Aetherboard/Build Full Battle (Edit Mode Preview)")]
        public static void BuildFullBattleInEditor()
        {
            if (Application.isPlaying)
            {
                Debug.LogWarning("Exit Play mode first.");
                return;
            }
            var existing = Object.FindObjectOfType<BattleDirector>();
            if (existing != null)
            {
                Debug.LogWarning("BattleDirector already exists in scene.");
                return;
            }
            BattleSceneBuilder.Build();
            Debug.Log("Aetherboard: Battle scene built in editor (use Play to test).");
        }

        [MenuItem("Aetherboard/Open Setup Guide")]
        public static void OpenSetupGuide() => OpenDoc("UNITY_SETUP.md");

        [MenuItem("Aetherboard/Open Quest Build Guide")]
        public static void OpenQuestGuide() => OpenDoc("QUEST_BUILD.md");

        [MenuItem("Aetherboard/Open PR Merge Guide")]
        public static void OpenPrMergeGuide() => OpenDoc("PR_MERGE.md");

        [MenuItem("Aetherboard/Open URP Setup Guide")]
        public static void OpenUrpGuide() => OpenDoc("URP_SETUP.md");

        [MenuItem("Aetherboard/Open Art Assets Guide")]
        public static void OpenArtGuide() => OpenDoc("ART_ASSETS.md");

        [MenuItem("Aetherboard/Open Quest Verification Guide")]
        public static void OpenQuestVerificationGuide() => OpenDoc("QUEST_VERIFICATION.md");

        private static void OpenDoc(string filename)
        {
            var path = System.IO.Path.GetFullPath(
                System.IO.Path.Combine(Application.dataPath, $"../../docs/{filename}"));
            if (System.IO.File.Exists(path)) EditorUtility.RevealInFinder(path);
            else Debug.LogWarning($"{filename} not found.");
        }
    }
}
#endif
