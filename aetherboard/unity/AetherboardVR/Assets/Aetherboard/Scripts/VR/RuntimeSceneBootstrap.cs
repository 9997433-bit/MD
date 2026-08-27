using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public static class AetherboardRuntimeLoader
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void OnAfterSceneLoad()
        {
            if (Object.FindObjectOfType<BattleDirector>() != null) return;
            if (Object.FindObjectOfType<RuntimeSceneBootstrap>() != null) return;
            var bootstrap = new GameObject("AetherboardBootstrap");
            bootstrap.AddComponent<RuntimeSceneBootstrap>();
        }
    }

    public class RuntimeSceneBootstrap : MonoBehaviour
    {
        [SerializeField] private string bossId = "earth";
        [SerializeField] private bool seatedMode = true;
        [SerializeField] private float tableDistance = 1.1f;
        [SerializeField] private XRRigSource rigSource = XRRigSource.Auto;

        private void Start()
        {
            bossId = BattleBossPrefs.LoadBoss(bossId);
            BattleSceneBuilder.Build(bossId, seatedMode, tableDistance, rigSource);
            var rigLabel = XRRigFactory.LastRigSource switch
            {
                XRRigSource.Prefab => "XR Prefab",
                _ => XRRigFactory.XrActive ? "XR Procedural" : "Desktop"
            };
            Debug.Log($"[Aetherboard] Ready ({rigLabel}, table={GetTableSourceLabel()}). C=双人 | Tab=切换 | H/N联机 | RMB=技能环");
        }

        private static string GetTableSourceLabel() =>
            BattlePrefabLibrary.HasPrefabs ? "Prefab" : "Procedural";
    }
}
