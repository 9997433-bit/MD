using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Shared gaze / VR ray helpers for skill ring, pieces, and board cells.
    /// </summary>
    public static class VRRaycastUtility
    {
        public const float MaxDistance = 8f;

        public static Ray CenterEyeRay(Camera cam = null)
        {
            cam ??= Camera.main;
            return cam != null
                ? cam.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0f))
                : default;
        }

        public static bool TryHitSkillChip(Ray ray, out SkillChip chip, out RaycastHit hit)
        {
            chip = null;
            if (!Physics.Raycast(ray, out hit, MaxDistance)) return false;
            chip = hit.collider.GetComponentInParent<SkillChip>();
            return chip != null;
        }

        public static bool TryHitBoard(Ray ray, out PieceToken piece, out GridCell cell, out RaycastHit hit)
        {
            piece = null;
            cell = null;
            if (!Physics.Raycast(ray, out hit, MaxDistance)) return false;
            piece = hit.collider.GetComponentInParent<PieceToken>();
            cell = hit.collider.GetComponentInParent<GridCell>();
            return piece != null || cell != null;
        }
    }
}
