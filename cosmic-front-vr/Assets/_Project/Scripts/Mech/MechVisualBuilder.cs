using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Mech
{
    /// <summary>
    /// Builds distinct placeholder silhouettes per target mech model (no licensed shapes).
    /// </summary>
    public static class MechVisualBuilder
    {
        public static void Apply(Transform root, MechModelId modelId, TeamId team)
        {
            if (root == null)
            {
                return;
            }

            var def = MechModelCatalog.Get(modelId);
            var pitch = root.Find("YawPivot/PitchPivot") ?? root;
            ClearGenerated(pitch);

            var body = CreatePart(pitch, "Body_Gen", PrimitiveType.Cube, Vector3.zero, def.BodyScale, def.AccentColor);
            ApplyFactionTint(body, team, 0.35f);

            switch (modelId)
            {
                case MechModelId.Bastion:
                    CreatePart(pitch, "ShoulderL_Gen", PrimitiveType.Cube, new Vector3(-1.4f, 0.8f, 0f),
                        new Vector3(0.9f, 0.7f, 1.2f), def.AccentColor * 0.85f);
                    CreatePart(pitch, "ShoulderR_Gen", PrimitiveType.Cube, new Vector3(1.4f, 0.8f, 0f),
                        new Vector3(0.9f, 0.7f, 1.2f), def.AccentColor * 0.85f);
                    CreatePart(pitch, "Shield_Gen", PrimitiveType.Cube, new Vector3(-1.6f, 0f, 0.4f),
                        new Vector3(0.3f, 2.2f, 1.6f), new Color(0.4f, 0.55f, 0.45f));
                    CreatePart(pitch, "Cannon_Gen", PrimitiveType.Cylinder, new Vector3(1.3f, 0f, 1.2f),
                        new Vector3(0.35f, 1.4f, 0.35f), new Color(0.3f, 0.3f, 0.35f));
                    break;

                case MechModelId.Kestrel:
                    CreatePart(pitch, "ThrusterL_Gen", PrimitiveType.Capsule, new Vector3(-0.7f, -0.6f, -0.8f),
                        new Vector3(0.35f, 0.7f, 0.35f), def.AccentColor);
                    CreatePart(pitch, "ThrusterR_Gen", PrimitiveType.Capsule, new Vector3(0.7f, -0.6f, -0.8f),
                        new Vector3(0.35f, 0.7f, 0.35f), def.AccentColor);
                    CreatePart(pitch, "WingL_Gen", PrimitiveType.Cube, new Vector3(-1.1f, 0.3f, -0.2f),
                        new Vector3(0.15f, 0.4f, 1.4f), def.AccentColor * 0.9f);
                    CreatePart(pitch, "WingR_Gen", PrimitiveType.Cube, new Vector3(1.1f, 0.3f, -0.2f),
                        new Vector3(0.15f, 0.4f, 1.4f), def.AccentColor * 0.9f);
                    break;

                case MechModelId.Warden:
                    CreatePart(pitch, "Array_Gen", PrimitiveType.Sphere, new Vector3(0f, 1.2f, 0.2f),
                        new Vector3(0.7f, 0.5f, 0.7f), new Color(0.6f, 0.9f, 1f));
                    CreatePart(pitch, "BeamArm_Gen", PrimitiveType.Cylinder, new Vector3(1.0f, 0.2f, 0.8f),
                        new Vector3(0.25f, 1.0f, 0.25f), new Color(0.4f, 0.8f, 0.9f));
                    break;

                case MechModelId.Mediator:
                    CreatePart(pitch, "Projector_Gen", PrimitiveType.Cube, new Vector3(0f, 0.9f, 0.6f),
                        new Vector3(1.2f, 0.25f, 0.4f), new Color(0.75f, 0.8f, 1f));
                    CreatePart(pitch, "PauldronL_Gen", PrimitiveType.Cube, new Vector3(-1.1f, 0.6f, 0f),
                        new Vector3(0.6f, 0.5f, 0.8f), def.AccentColor);
                    CreatePart(pitch, "PauldronR_Gen", PrimitiveType.Cube, new Vector3(1.1f, 0.6f, 0f),
                        new Vector3(0.6f, 0.5f, 0.8f), def.AccentColor);
                    break;

                case MechModelId.Beacon:
                    CreatePart(pitch, "SensorDish_Gen", PrimitiveType.Sphere, new Vector3(0f, 1.3f, 0f),
                        new Vector3(0.9f, 0.35f, 0.9f), new Color(0.95f, 0.95f, 1f));
                    CreatePart(pitch, "Fin_Gen", PrimitiveType.Cube, new Vector3(0f, 0.2f, -1.0f),
                        new Vector3(0.1f, 1.2f, 0.8f), def.AccentColor);
                    CreatePart(pitch, "ScoutPod_Gen", PrimitiveType.Capsule, new Vector3(0f, -0.4f, 0.6f),
                        new Vector3(0.4f, 0.5f, 0.4f), new Color(0.8f, 0.85f, 1f));
                    break;
            }
        }

        private static void ClearGenerated(Transform pitch)
        {
            for (var i = pitch.childCount - 1; i >= 0; i--)
            {
                var child = pitch.GetChild(i);
                if (child.name.EndsWith("_Gen") || child.name == "Body")
                {
                    if (Application.isPlaying)
                    {
                        Object.Destroy(child.gameObject);
                    }
                    else
                    {
                        Object.DestroyImmediate(child.gameObject);
                    }
                }
            }
        }

        private static GameObject CreatePart(
            Transform parent,
            string name,
            PrimitiveType type,
            Vector3 localPos,
            Vector3 scale,
            Color color)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = scale;
            var col = go.GetComponent<Collider>();
            if (col != null)
            {
                if (Application.isPlaying)
                {
                    Object.Destroy(col);
                }
                else
                {
                    Object.DestroyImmediate(col);
                }
            }

            var renderer = go.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.sharedMaterial = new Material(
                    Shader.Find("Universal Render Pipeline/Lit")
                    ?? Shader.Find("Standard")
                    ?? Shader.Find("Diffuse")
                    ?? renderer.sharedMaterial.shader)
                {
                    color = color
                };
            }

            return go;
        }

        private static void ApplyFactionTint(GameObject body, TeamId team, float amount)
        {
            var renderer = body.GetComponent<Renderer>();
            if (renderer == null)
            {
                return;
            }

            var faction = FactionCatalog.GetPrimaryColor(team);
            var c = Color.Lerp(renderer.sharedMaterial.color, faction, amount);
            renderer.sharedMaterial.color = c;
        }
    }
}
