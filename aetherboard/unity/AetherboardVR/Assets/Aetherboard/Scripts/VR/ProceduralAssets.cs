using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Builds primitive meshes for cells, pieces, and telegraph rings at runtime.
    /// </summary>
    public static class ProceduralAssets
    {
        public static Material CreateUnlitMaterial(Color color)
        {
            var shader = Shader.Find("Universal Render Pipeline/Unlit")
                         ?? Shader.Find("Unlit/Color")
                         ?? Shader.Find("Standard");
            var mat = new Material(shader);
            mat.color = color;
            return mat;
        }

        public static GameObject CreateCell(Transform parent, float cellSize, float height)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "Cell";
            go.transform.SetParent(parent, false);
            go.transform.localScale = new Vector3(cellSize * 0.95f, 0.02f, cellSize * 0.95f);
            go.transform.localPosition = new Vector3(0, height, 0);
            return go;
        }

        public static GameObject CreatePiece(Transform parent, float cellSize)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "Piece";
            go.transform.SetParent(parent, false);
            var h = cellSize * 0.55f;
            go.transform.localScale = new Vector3(cellSize * 0.45f, h * 0.5f, cellSize * 0.45f);
            go.transform.localPosition = new Vector3(0, h * 0.5f, 0);
            return go;
        }

        public static GameObject CreatePreviewRing(Transform parent, float cellSize)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = "PreviewRing";
            go.transform.SetParent(parent, false);
            go.transform.localScale = new Vector3(cellSize * 0.9f, 0.005f, cellSize * 0.9f);
            var col = go.GetComponent<Collider>();
            if (col != null) Object.Destroy(col);
            return go;
        }

        public static GameObject CreateTableBase(Transform parent, float size)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "TableBase";
            go.transform.SetParent(parent, false);
            go.transform.localScale = new Vector3(size, 0.04f, size);
            go.transform.localPosition = new Vector3(0, -0.02f, 0);
            var renderer = go.GetComponent<Renderer>();
            renderer.sharedMaterial = CreateUnlitMaterial(new Color(0.12f, 0.16f, 0.22f));
            return go;
        }

        public static GameObject CreateBossMarker(Transform parent, float cellSize)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = "BossMarker";
            go.transform.SetParent(parent, false);
            go.transform.localScale = Vector3.one * cellSize * 0.7f;
            var renderer = go.GetComponent<Renderer>();
            renderer.sharedMaterial = CreateUnlitMaterial(new Color(0.85f, 0.2f, 0.15f));
            var col = go.GetComponent<Collider>();
            if (col != null) Object.Destroy(col);
            return go;
        }
    }
}
