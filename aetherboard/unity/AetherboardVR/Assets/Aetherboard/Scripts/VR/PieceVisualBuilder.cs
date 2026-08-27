using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Builds job-themed piece silhouettes from primitives or external models.
    /// </summary>
    public class PieceVisualBuilder : MonoBehaviour
    {
        [SerializeField] private Transform visualRoot;
        [SerializeField] private float scale = 1f;

        private JobType _lastJob = (JobType)(-1);
        private GameObject _externalInstance;

        public Renderer PrimaryRenderer { get; private set; }

        public void Apply(JobType job)
        {
            if (_lastJob == job && PrimaryRenderer != null) return;
            _lastJob = job;
            ClearVisuals();

            var external = BattleArtCatalog.LoadPieceModel(job);
            if (external != null)
            {
                BuildFromExternal(external, job);
                return;
            }

            BuildProcedural(job);
        }

        private void BuildFromExternal(GameObject prefab, JobType job)
        {
            EnsureRoot();
            _externalInstance = Instantiate(prefab, visualRoot);
            _externalInstance.transform.localPosition = Vector3.zero;
            _externalInstance.transform.localRotation = Quaternion.identity;
            _externalInstance.transform.localScale = Vector3.one * scale;
            PrimaryRenderer = _externalInstance.GetComponentInChildren<Renderer>();
            TintRenderers(job);
        }

        private void BuildProcedural(JobType job)
        {
            EnsureRoot();
            var color = BattleArtPalette.ForJob(job);
            var accent = BattleArtPalette.CreateEmissiveMaterial(color, 0.9f);
            var bodyMat = BattleArtPalette.CreateSurfaceMaterial(color, 0.35f, 0.65f);

            switch (job)
            {
                case JobType.Knight:
                    PrimaryRenderer = AddPrimitive(PrimitiveType.Capsule, "Body",
                        new Vector3(0.042f, 0.055f, 0.042f), new Vector3(0, 0.05f, 0), bodyMat);
                    AddPrimitive(PrimitiveType.Cube, "Shield",
                        new Vector3(0.05f, 0.05f, 0.008f), new Vector3(0.03f, 0.05f, 0), accent);
                    break;
                case JobType.WhiteMage:
                    PrimaryRenderer = AddPrimitive(PrimitiveType.Sphere, "Orb",
                        new Vector3(0.05f, 0.05f, 0.05f), new Vector3(0, 0.06f, 0), accent);
                    AddPrimitive(PrimitiveType.Cylinder, "Staff",
                        new Vector3(0.012f, 0.06f, 0.012f), new Vector3(-0.02f, 0.05f, 0), bodyMat);
                    break;
                case JobType.BlackMage:
                    PrimaryRenderer = AddPrimitive(PrimitiveType.Cylinder, "Hat",
                        new Vector3(0.05f, 0.04f, 0.05f), new Vector3(0, 0.055f, 0), bodyMat);
                    AddPrimitive(PrimitiveType.Sphere, "Core",
                        new Vector3(0.028f, 0.028f, 0.028f), new Vector3(0, 0.08f, 0), accent);
                    break;
                case JobType.Bard:
                    PrimaryRenderer = AddPrimitive(PrimitiveType.Cylinder, "Body",
                        new Vector3(0.04f, 0.05f, 0.04f), new Vector3(0, 0.05f, 0), bodyMat);
                    AddPrimitive(PrimitiveType.Cylinder, "Lyre",
                        new Vector3(0.055f, 0.006f, 0.03f), new Vector3(0.02f, 0.07f, 0), accent);
                    break;
                default:
                    PrimaryRenderer = AddPrimitive(PrimitiveType.Cylinder, "Body",
                        new Vector3(0.045f, 0.05f, 0.045f), new Vector3(0, 0.05f, 0), bodyMat);
                    break;
            }
        }

        private void EnsureRoot()
        {
            if (visualRoot != null) return;
            var root = new GameObject("Visual");
            root.transform.SetParent(transform, false);
            visualRoot = root.transform;
        }

        private Renderer AddPrimitive(
            PrimitiveType type, string name, Vector3 localScale, Vector3 localPos, Material mat)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.SetParent(visualRoot, false);
            go.transform.localScale = localScale * scale;
            go.transform.localPosition = localPos;
            var col = go.GetComponent<Collider>();
            if (col != null) DestroyCollider(col);
            go.GetComponent<Renderer>().sharedMaterial = mat;
            return go.GetComponent<Renderer>();
        }

        private void TintRenderers(JobType job)
        {
            if (_externalInstance == null) return;
            var tint = BattleArtPalette.ForJob(job);
            foreach (var r in _externalInstance.GetComponentsInChildren<Renderer>())
            {
                if (r.sharedMaterial == null) continue;
                r.material.color = Color.Lerp(r.material.color, tint, 0.35f);
            }
        }

        private void ClearVisuals()
        {
            EnsureRoot();
            if (_externalInstance != null)
            {
                Destroy(_externalInstance);
                _externalInstance = null;
            }

            for (var i = visualRoot.childCount - 1; i >= 0; i--)
                Destroy(visualRoot.GetChild(i).gameObject);

            PrimaryRenderer = null;
        }

        private static void DestroyCollider(Collider col)
        {
#if UNITY_EDITOR
            if (!Application.isPlaying)
            {
                Object.DestroyImmediate(col);
                return;
            }
#endif
            Object.Destroy(col);
        }
    }
}
