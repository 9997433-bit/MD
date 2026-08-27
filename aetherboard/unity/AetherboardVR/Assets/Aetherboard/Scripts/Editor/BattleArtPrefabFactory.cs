#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;
using Aetherboard.VR;
using Aetherboard.Core;

namespace Aetherboard.Editor
{
    /// <summary>
    /// Builds FF14-inspired styled prefabs (materials + composite meshes).
    /// </summary>
    public static class BattleArtPrefabFactory
    {
        private const string ResourceDir = "Assets/Aetherboard/Resources/Aetherboard";
        private const string MaterialDir = ResourceDir + "/Materials";
        private const string ModelDir = ResourceDir + "/Art/Models";

        public static void InstallStyledPrefabs()
        {
            Directory.CreateDirectory(ResourceDir);
            Directory.CreateDirectory(MaterialDir);
            Directory.CreateDirectory(ModelDir);

            var tableMat = SaveMaterial("Mat_TableStone", BattleArtPalette.TableStone, 0.1f, 0.4f);
            var rimMat = SaveMaterial("Mat_TableRim", BattleArtPalette.TableRim, 0.55f, 0.7f);
            var cellMat = SaveMaterial("Mat_Cell", BattleArtPalette.CellNormal, 0.2f, 0.5f);
            var insetMat = SaveMaterial("Mat_CellInset", BattleArtPalette.CellInset, 0.15f, 0.65f);
            var ringMat = SaveMaterial("Mat_PreviewRing", new Color(0.85f, 0.55f, 0.12f, 0.75f), 0.3f, 0.8f);
            ringMat.EnableKeyword("_EMISSION");
            ringMat.SetColor("_EmissionColor", new Color(0.6f, 0.35f, 0.05f));

            SavePrefab(BuildTableBase(tableMat, rimMat), ResourceDir + "/TableBase.prefab");
            SavePrefab(BuildGridCell(cellMat, insetMat), ResourceDir + "/GridCell.prefab");
            SavePrefab(BuildPieceToken(), ResourceDir + "/PieceToken.prefab");
            SavePrefab(BuildPreviewRing(ringMat), ResourceDir + "/PreviewRing.prefab");
            SavePrefab(BuildBossMarker(), ResourceDir + "/BossMarker.prefab");

            AssetDatabase.Refresh();
            Debug.Log(
                "Aetherboard: Styled battle prefabs installed.\n" +
                $"Materials → {MaterialDir}\n" +
                $"Drop custom FBX into {ModelDir} as Piece_Knight etc. (see ART_ASSETS.md)");
        }

        private static Material SaveMaterial(string name, Color color, float metallic, float smoothness)
        {
            var path = $"{MaterialDir}/{name}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (mat == null)
            {
                mat = BattleArtPalette.CreateSurfaceMaterial(color, metallic, smoothness);
                AssetDatabase.CreateAsset(mat, path);
            }
            else
            {
                mat.color = color;
                if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", metallic);
                if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", smoothness);
                EditorUtility.SetDirty(mat);
            }
            return mat;
        }

        private static GameObject BuildTableBase(Material slab, Material rim)
        {
            var external = BattleArtCatalog.LoadTableBase();
            if (external != null)
            {
                var inst = Object.Instantiate(external);
                inst.name = "TableBase";
                return inst;
            }

            var root = new GameObject("TableBase");
            var slabGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
            slabGo.name = "Slab";
            slabGo.transform.SetParent(root.transform, false);
            slabGo.transform.localScale = new Vector3(0.92f, 0.045f, 0.92f);
            slabGo.transform.localPosition = new Vector3(0, -0.022f, 0);
            slabGo.GetComponent<Renderer>().sharedMaterial = slab;
            Object.DestroyImmediate(slabGo.GetComponent<Collider>());

            foreach (var side in new[] { Vector3.forward, Vector3.back, Vector3.left, Vector3.right })
            {
                var rimGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
                rimGo.name = "Rim";
                rimGo.transform.SetParent(root.transform, false);
                rimGo.transform.localScale = side.z != 0
                    ? new Vector3(0.94f, 0.055f, 0.012f)
                    : new Vector3(0.012f, 0.055f, 0.94f);
                rimGo.transform.localPosition = side * 0.46f + Vector3.down * 0.01f;
                rimGo.GetComponent<Renderer>().sharedMaterial = rim;
                Object.DestroyImmediate(rimGo.GetComponent<Collider>());
            }

            return root;
        }

        private static GameObject BuildGridCell(Material cell, Material inset)
        {
            var external = BattleArtCatalog.LoadGridCell();
            if (external != null)
            {
                var inst = Object.Instantiate(external);
                inst.name = "GridCell";
                if (inst.GetComponent<GridCell>() == null) inst.AddComponent<GridCell>();
                return inst;
            }

            var root = GameObject.CreatePrimitive(PrimitiveType.Cube);
            root.name = "GridCell";
            root.transform.localScale = new Vector3(0.114f, 0.018f, 0.114f);
            root.GetComponent<Renderer>().sharedMaterial = cell;

            var insetGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
            insetGo.name = "Inset";
            insetGo.transform.SetParent(root.transform, false);
            insetGo.transform.localScale = new Vector3(0.82f, 0.35f, 0.82f);
            insetGo.transform.localPosition = new Vector3(0, 0.55f, 0);
            insetGo.GetComponent<Renderer>().sharedMaterial = inset;
            Object.DestroyImmediate(insetGo.GetComponent<Collider>());

            var gridCell = root.AddComponent<GridCell>();
            gridCell.InitProcedural(0, 0, root.GetComponent<Renderer>());
            return root;
        }

        private static GameObject BuildPieceToken()
        {
            var root = new GameObject("PieceToken");
            root.AddComponent<PieceVisualBuilder>();
            root.AddComponent<PieceToken>();
            return root;
        }

        private static GameObject BuildPreviewRing(Material mat)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "PreviewRing";
            go.transform.localScale = new Vector3(0.108f, 0.004f, 0.108f);
            Object.DestroyImmediate(go.GetComponent<Collider>());
            go.GetComponent<Renderer>().sharedMaterial = mat;
            return go;
        }

        private static GameObject BuildBossMarker()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = "BossMarker";
            go.transform.localScale = Vector3.one * 0.08f;
            var mat = BattleArtPalette.CreateEmissiveMaterial(new Color(0.9f, 0.15f, 0.1f), 1.5f);
            go.GetComponent<Renderer>().sharedMaterial = mat;
            Object.DestroyImmediate(go.GetComponent<Collider>());
            return go;
        }

        private static void SavePrefab(GameObject template, string path)
        {
            if (File.Exists(path)) AssetDatabase.DeleteAsset(path);
            PrefabUtility.SaveAsPrefabAsset(template, path);
            Object.DestroyImmediate(template);
        }
    }
}
#endif
