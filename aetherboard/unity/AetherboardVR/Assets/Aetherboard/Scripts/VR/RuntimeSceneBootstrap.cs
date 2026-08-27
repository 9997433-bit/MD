using UnityEngine;
using UnityEngine.SceneManagement;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Auto-spawns the full battle scene when no BattleDirector exists (press Play in empty scene).
    /// </summary>
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

    /// <summary>
    /// Procedurally builds table, HUD, camera, and battle systems.
    /// </summary>
    public class RuntimeSceneBootstrap : MonoBehaviour
    {
        [SerializeField] private string bossId = "earth";
        [SerializeField] private bool seatedMode = true;
        [SerializeField] private float tableDistance = 1.1f;

        private void Start()
        {
            BuildScene();
        }

        public void BuildScene()
        {
            var root = new GameObject("BattleRoot");
            root.transform.position = new Vector3(0, seatedMode ? 0.75f : 1.0f, tableDistance);

            var director = root.AddComponent<BattleDirector>();
            var tableView = root.AddComponent<BattleTableView>();
            var telegraph = root.AddComponent<TelegraphVFXController>();
            var bossView = root.AddComponent<BossHologramView>();
            root.AddComponent<VRBattleBootstrap>();

            tableView.BuildProcedural(root.transform, director);
            telegraph.InitializeProcedural(tableView);
            bossView.InitializeProcedural(root.transform);

            var hud = new GameObject("BattleHUD");
            hud.transform.SetParent(root.transform, false);
            hud.transform.localPosition = new Vector3(0, 0.35f, -0.55f);
            var hudCtrl = hud.AddComponent<BattleHUDController>();
            hudCtrl.Bind(director);

            var desktop = root.AddComponent<DesktopBattleInput>();
            desktop.Bind(director, tableView);

            SetupCamera(root.transform.position);

            director.SetBoss(bossId);
            Debug.Log("[Aetherboard] Runtime scene ready. Desktop: click piece → click cell. Keys: E=End Phase, A=Auto.");
        }

        private static void SetupCamera(Vector3 lookTarget)
        {
            var cam = Camera.main;
            if (cam == null)
            {
                var camGo = new GameObject("Main Camera");
                cam = camGo.AddComponent<Camera>();
                camGo.tag = "MainCamera";
                camGo.AddComponent<AudioListener>();
            }
            cam.transform.position = lookTarget + new Vector3(0, 0.65f, -0.85f);
            cam.transform.LookAt(lookTarget + Vector3.up * 0.05f);

            if (Object.FindObjectOfType<Light>() == null)
            {
                var lightGo = new GameObject("Directional Light");
                var light = lightGo.AddComponent<Light>();
                light.type = LightType.Directional;
                light.intensity = 1.1f;
                lightGo.transform.rotation = Quaternion.Euler(50, -30, 0);
            }
        }
    }
}
