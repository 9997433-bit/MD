#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    /// <summary>
    /// Validates external art inventory and converts dropped FBX files into Resources prefabs.
    /// </summary>
    public static class BattleArtImportWizard
    {
        private const string ModelDir = "Assets/Aetherboard/Resources/Aetherboard/Art/Models";

        private static readonly string[] ExpectedPrefabs =
        {
            "Piece_Knight", "Piece_WhiteMage", "Piece_BlackMage", "Piece_Bard",
            "Table_Base", "Grid_Cell", "Boss_earth", "Boss_wind"
        };

        [MenuItem("Aetherboard/Art/Open Models Folder")]
        public static void OpenModelsFolder()
        {
            Directory.CreateDirectory(ModelDir);
            AssetDatabase.Refresh();
            EditorUtility.RevealInFinder(Path.GetFullPath(ModelDir));
        }

        [MenuItem("Aetherboard/Art/Validate Art Inventory")]
        public static void ValidateInventory()
        {
            Directory.CreateDirectory(ModelDir);
            var report = BattleArtCatalog.BuildInventoryReport();
            Debug.Log($"Aetherboard art inventory:\n{report}");
        }

        [MenuItem("Aetherboard/Art/Convert FBX in Models Folder to Prefabs")]
        public static void ConvertFbxInModelsFolder()
        {
            Directory.CreateDirectory(ModelDir);
            var converted = 0;
            foreach (var fbxPath in Directory.GetFiles(ModelDir, "*.fbx", SearchOption.TopDirectoryOnly))
            {
                var baseName = Path.GetFileNameWithoutExtension(fbxPath);
                if (!ExpectedPrefabs.Contains(baseName))
                {
                    Debug.LogWarning($"Aetherboard: Skipping {baseName}.fbx — name not in ART_ASSETS.md convention.");
                    continue;
                }

                if (ConvertFbxToPrefab(fbxPath, $"{ModelDir}/{baseName}.prefab"))
                    converted++;
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"Aetherboard: Converted {converted} FBX file(s). Run Validate Art Inventory to confirm.");
        }

        [MenuItem("Aetherboard/Art/Convert Selected FBX to Prefab...")]
        public static void ConvertSelectedFbx()
        {
            var fbx = Selection.activeObject as GameObject;
            if (fbx == null)
            {
                Debug.LogWarning("Aetherboard: Select an imported FBX model in the Project window.");
                return;
            }

            var assetPath = AssetDatabase.GetAssetPath(fbx);
            if (!assetPath.EndsWith(".fbx", System.StringComparison.OrdinalIgnoreCase))
            {
                Debug.LogWarning("Aetherboard: Selected asset is not an FBX.");
                return;
            }

            var baseName = Path.GetFileNameWithoutExtension(assetPath);
            var choices = ExpectedPrefabs.ToList();
            var index = choices.IndexOf(baseName);
            if (index < 0)
            {
                index = EditorUtility.DisplayDialogComplex(
                    "Aetherboard Art Import",
                    $"FBX name '{baseName}' is not standard. Pick a target prefab name:",
                    "Piece_Knight", "Cancel", "Table_Base");
                if (index == 1) return;
                baseName = index == 0 ? "Piece_Knight" : "Table_Base";
            }

            Directory.CreateDirectory(ModelDir);
            var prefabPath = $"{ModelDir}/{baseName}.prefab";
            if (ConvertFbxToPrefab(assetPath, prefabPath))
            {
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh();
                Debug.Log($"Aetherboard: Created {prefabPath}");
            }
        }

        [MenuItem("Aetherboard/Art/Convert Selected FBX to Prefab...", true)]
        private static bool ValidateConvertSelected()
        {
            var path = Selection.activeObject != null ? AssetDatabase.GetAssetPath(Selection.activeObject) : null;
            return !string.IsNullOrEmpty(path) && path.EndsWith(".fbx", System.StringComparison.OrdinalIgnoreCase);
        }

        private static bool ConvertFbxToPrefab(string fbxAssetPath, string prefabPath)
        {
            var source = AssetDatabase.LoadAssetAtPath<GameObject>(fbxAssetPath);
            if (source == null)
            {
                Debug.LogError($"Aetherboard: Failed to load {fbxAssetPath}");
                return false;
            }

            var instance = PrefabUtility.InstantiatePrefab(source) as GameObject;
            if (instance == null) instance = Object.Instantiate(source);

            instance.name = Path.GetFileNameWithoutExtension(prefabPath);
            NormalizeModelTransform(instance);

            if (File.Exists(prefabPath)) AssetDatabase.DeleteAsset(prefabPath);
            PrefabUtility.SaveAsPrefabAsset(instance, prefabPath);
            Object.DestroyImmediate(instance);
            return true;
        }

        private static void NormalizeModelTransform(GameObject root)
        {
            root.transform.localPosition = Vector3.zero;
            root.transform.localRotation = Quaternion.identity;
            root.transform.localScale = Vector3.one;

            var renderers = root.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) return;

            var bounds = renderers[0].bounds;
            foreach (var r in renderers) bounds.Encapsulate(r.bounds);

            var height = bounds.size.y;
            if (height > 0.001f && Mathf.Abs(height - 0.1f) > 0.02f)
            {
                var scale = 0.1f / height;
                root.transform.localScale = Vector3.one * scale;
            }
        }
    }
}
#endif
