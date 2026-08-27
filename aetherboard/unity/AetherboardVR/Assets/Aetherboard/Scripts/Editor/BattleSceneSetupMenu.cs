#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    public static class BattleSceneSetupMenu
    {
        [MenuItem("Aetherboard/Create Battle Root")]
        public static void CreateBattleRoot()
        {
            var root = new GameObject("BattleRoot");
            root.AddComponent<BattleDirector>();
            root.AddComponent<BattleTableView>();
            root.AddComponent<TelegraphVFXController>();
            root.AddComponent<BossHologramView>();
            root.AddComponent<VRBattleBootstrap>();
            Selection.activeGameObject = root;
            Debug.Log("Aetherboard: BattleRoot created. Assign prefabs in Inspector.");
        }

        [MenuItem("Aetherboard/Open Setup Guide")]
        public static void OpenGuide()
        {
            var path = System.IO.Path.GetFullPath(
                System.IO.Path.Combine(Application.dataPath, "../../docs/UNITY_SETUP.md"));
            if (System.IO.File.Exists(path))
                EditorUtility.RevealInFinder(path);
            else
                Debug.LogWarning("UNITY_SETUP.md not found at " + path);
        }
    }
}
#endif
