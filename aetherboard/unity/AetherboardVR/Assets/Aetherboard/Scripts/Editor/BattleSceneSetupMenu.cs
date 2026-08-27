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

        [MenuItem("Aetherboard/Create Battle Root")]
        public static void CreateBattleRoot()
        {
            var root = new GameObject("BattleRoot");
            root.AddComponent<RuntimeSceneBootstrap>();
            Selection.activeGameObject = root;
            Debug.Log("Aetherboard: BattleRoot with RuntimeSceneBootstrap created. Press Play to build table.");
        }

        [MenuItem("Aetherboard/Create Battle Scene File")]
        public static void CreateBattleScene()
        {
            System.IO.Directory.CreateDirectory("Assets/Aetherboard/Scenes");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            var root = new GameObject("AetherboardBootstrap");
            root.AddComponent<RuntimeSceneBootstrap>();
            EditorSceneManager.SaveScene(scene, ScenePath);
            var scenes = new[] { ScenePath };
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            Debug.Log($"Aetherboard: Scene saved to {ScenePath} and added to Build Settings.");
        }

        [MenuItem("Aetherboard/Open Setup Guide")]
        public static void OpenSetupGuide() => OpenDoc("UNITY_SETUP.md");

        [MenuItem("Aetherboard/Open Quest Build Guide")]
        public static void OpenQuestGuide() => OpenDoc("QUEST_BUILD.md");

        private static void OpenDoc(string filename)
        {
            var path = System.IO.Path.GetFullPath(
                System.IO.Path.Combine(Application.dataPath, $"../../docs/{filename}"));
            if (System.IO.File.Exists(path))
                EditorUtility.RevealInFinder(path);
            else
                Debug.LogWarning($"{filename} not found at " + path);
        }
    }
}
#endif
