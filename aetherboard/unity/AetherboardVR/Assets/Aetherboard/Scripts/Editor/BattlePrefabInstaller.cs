#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;

namespace Aetherboard.Editor
{
    public static class BattlePrefabInstaller
    {
        private const string ResourceDir = "Assets/Aetherboard/Resources/Aetherboard";
        private const string GridCellPath = ResourceDir + "/GridCell.prefab";
        private const string PieceTokenPath = ResourceDir + "/PieceToken.prefab";
        private const string TableBasePath = ResourceDir + "/TableBase.prefab";
        private const string PreviewRingPath = ResourceDir + "/PreviewRing.prefab";

        [MenuItem("Aetherboard/Install Battle Table Prefabs")]
        public static void InstallBattleTablePrefabs() =>
            BattleArtPrefabFactory.InstallStyledPrefabs();

        [MenuItem("Aetherboard/Install Basic Battle Table Prefabs (Legacy)")]
        public static void InstallLegacyBattleTablePrefabs()
        {
            Directory.CreateDirectory(ResourceDir);

            SavePrefab(CreateGridCellTemplate(), GridCellPath);
            SavePrefab(CreatePieceTokenTemplate(), PieceTokenPath);
            SavePrefab(CreateTableBaseTemplate(), TableBasePath);
            SavePrefab(CreatePreviewRingTemplate(), PreviewRingPath);

            AssetDatabase.Refresh();
            Debug.Log(
                "Aetherboard: Battle table prefabs installed.\n" +
                $"  {GridCellPath}\n  {PieceTokenPath}\n  {TableBasePath}\n  {PreviewRingPath}\n" +
                "运行时 BattleTableView 将优先使用 Prefab（无则回退程序化几何体）。");
        }

        [MenuItem("Aetherboard/Install Battle Table Prefabs", true)]
        private static bool InstallBattleTablePrefabsValidate() => !Application.isPlaying;

        private static void SavePrefab(GameObject template, string path)
        {
            if (File.Exists(path))
                AssetDatabase.DeleteAsset(path);

            var prefab = PrefabUtility.SaveAsPrefabAsset(template, path);
            Object.DestroyImmediate(template);
            if (prefab == null)
                Debug.LogError($"Aetherboard: Failed to save prefab {path}");
        }

        private static GameObject CreateGridCellTemplate()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "GridCell";
            go.transform.localScale = new Vector3(0.114f, 0.02f, 0.114f);
            var cell = go.AddComponent<GridCell>();
            cell.InitProcedural(0, 0, go.GetComponent<Renderer>());
            return go;
        }

        private static GameObject CreatePieceTokenTemplate()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "PieceToken";
            go.transform.localScale = new Vector3(0.054f, 0.033f, 0.054f);
            var token = go.AddComponent<PieceToken>();
            token.InitProcedural(go.GetComponent<Renderer>());
            return go;
        }

        private static GameObject CreateTableBaseTemplate()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "TableBase";
            go.transform.localScale = new Vector3(0.9f, 0.04f, 0.9f);
            go.transform.localPosition = new Vector3(0, -0.02f, 0);
            go.GetComponent<Renderer>().sharedMaterial =
                new Material(Shader.Find("Standard") ?? Shader.Find("Unlit/Color"))
                {
                    color = new Color(0.12f, 0.16f, 0.22f)
                };
            return go;
        }

        private static GameObject CreatePreviewRingTemplate()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "PreviewRing";
            go.transform.localScale = new Vector3(0.108f, 0.005f, 0.108f);
            Object.DestroyImmediate(go.GetComponent<Collider>());
            go.GetComponent<Renderer>().sharedMaterial =
                new Material(Shader.Find("Standard") ?? Shader.Find("Unlit/Color"))
                {
                    color = new Color(0.7f, 0.45f, 0.1f, 0.6f)
                };
            return go;
        }
    }
}
#endif
