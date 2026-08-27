using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Shared palette and material helpers for battle table art (FF14-inspired tones).
    /// </summary>
    public static class BattleArtPalette
    {
        public static readonly Color TableStone = new(0.1f, 0.12f, 0.16f);
        public static readonly Color TableRim = new(0.28f, 0.22f, 0.14f);
        public static readonly Color CellNormal = new(0.16f, 0.2f, 0.28f);
        public static readonly Color CellBoss = new(0.32f, 0.1f, 0.1f);
        public static readonly Color CellInset = new(0.22f, 0.26f, 0.34f);

        public static readonly Color Knight = new(0.25f, 0.52f, 0.88f);
        public static readonly Color WhiteMage = new(0.3f, 0.82f, 0.45f);
        public static readonly Color BlackMage = new(0.58f, 0.28f, 0.82f);
        public static readonly Color Bard = new(0.92f, 0.5f, 0.12f);

        public static Color ForJob(Aetherboard.Core.JobType job) => job switch
        {
            Aetherboard.Core.JobType.Knight => Knight,
            Aetherboard.Core.JobType.WhiteMage => WhiteMage,
            Aetherboard.Core.JobType.BlackMage => BlackMage,
            Aetherboard.Core.JobType.Bard => Bard,
            _ => Color.white
        };

        public static Material CreateSurfaceMaterial(Color color, float metallic = 0.15f, float smoothness = 0.55f)
        {
            var shader = Shader.Find("Universal Render Pipeline/Lit")
                         ?? Shader.Find("Standard")
                         ?? Shader.Find("Unlit/Color");
            var mat = new Material(shader);
            mat.color = color;
            if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", metallic);
            if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", smoothness);
            return mat;
        }

        public static Material CreateEmissiveMaterial(Color color, float intensity = 1.2f)
        {
            var mat = CreateSurfaceMaterial(color, 0.05f, 0.35f);
            var emissive = color * intensity;
            if (mat.HasProperty("_EmissionColor"))
            {
                mat.EnableKeyword("_EMISSION");
                mat.SetColor("_EmissionColor", emissive);
            }
            return mat;
        }
    }
}
