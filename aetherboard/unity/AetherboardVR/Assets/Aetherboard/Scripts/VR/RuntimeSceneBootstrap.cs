using UnityEngine;
using UnityEngine.SceneManagement;
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

        private BattleDirector _director;
        private SkillRingController _skillRing;

        private void Start() => BuildScene();

        public void BuildScene()
        {
            var tableCenter = new Vector3(0, seatedMode ? 0.75f : 1.0f, tableDistance);

            var root = new GameObject("BattleRoot");
            root.transform.position = tableCenter;

            _director = root.AddComponent<BattleDirector>();
            var tableView = root.AddComponent<BattleTableView>();
            var telegraph = root.AddComponent<TelegraphVFXController>();
            var bossView = root.AddComponent<BossHologramView>();
            root.AddComponent<VRBattleBootstrap>();

            tableView.BuildProcedural(root.transform, _director);
            telegraph.InitializeProcedural(tableView);
            bossView.InitializeProcedural(root.transform);

            _skillRing = root.AddComponent<SkillRingController>();
            _skillRing.Initialize(_director, tableView, root.transform);

            var hud = new GameObject("BattleHUD");
            hud.transform.SetParent(root.transform, false);
            hud.transform.localPosition = new Vector3(0, 0.35f, -0.55f);
            var hudCtrl = hud.AddComponent<BattleHUDController>();
            hudCtrl.Bind(_director);

            var desktop = root.AddComponent<DesktopBattleInput>();
            desktop.Bind(_director, tableView, _skillRing);

            root.AddComponent<VRInputBridge>().Bind(_director, tableView, _skillRing, desktop);

            XRRigFactory.EnsureLighting();
            XRRigFactory.CreateRig(tableCenter, seatedMode, out _);

            _director.SetBoss(bossId);
            var mode = XRRigFactory.XrActive ? "XR" : "Desktop";
            Debug.Log($"[Aetherboard] Ready ({mode}). LMB: select/move | RMB: skills | E/A/1/2");
        }
    }
}
