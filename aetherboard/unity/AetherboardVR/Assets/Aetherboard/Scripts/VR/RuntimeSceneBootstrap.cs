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

        private void Start()
        {
            BattleSceneBuilder.Build(bossId, seatedMode, tableDistance);
            var mode = XRRigFactory.XrActive ? "XR" : "Desktop";
            Debug.Log($"[Aetherboard] Ready ({mode}). C=双人 | Tab=切换玩家 | RMB=技能环");
        }
    }
}
