using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Shared scene build logic for runtime bootstrap and editor scene creation.
    /// </summary>
    public static class BattleSceneBuilder
    {
        public static BattleDirector Build(
            string bossId = "earth",
            bool seatedMode = true,
            float tableDistance = 1.1f)
        {
            var tableCenter = new Vector3(0, seatedMode ? 0.75f : 1.0f, tableDistance);

            var root = new GameObject("BattleRoot");
            root.transform.position = tableCenter;

            var director = root.AddComponent<BattleDirector>();
            var tableView = root.AddComponent<BattleTableView>();
            var telegraph = root.AddComponent<TelegraphVFXController>();
            var bossView = root.AddComponent<BossHologramView>();
            root.AddComponent<VRBattleBootstrap>();

            tableView.BuildProcedural(root.transform, director);
            telegraph.InitializeProcedural(tableView);
            bossView.InitializeProcedural(root.transform);

            var skillRing = root.AddComponent<SkillRingController>();
            skillRing.Initialize(director, tableView, root.transform);

            var coop = root.AddComponent<CoopController>();

            var hudGo = new GameObject("BattleHUD");
            hudGo.transform.SetParent(root.transform, false);
            hudGo.transform.localPosition = new Vector3(0, 0.35f, -0.55f);
            var hud = hudGo.AddComponent<BattleHUDController>();
            hud.Bind(director, coop);

            var desktop = root.AddComponent<DesktopBattleInput>();
            desktop.Bind(director, tableView, skillRing, coop);

            root.AddComponent<VRInputBridge>().Bind(director, tableView, skillRing, desktop, coop);

            var audioGo = new GameObject("BattleAudio");
            audioGo.transform.SetParent(root.transform, false);
            audioGo.AddComponent<AudioSource>();
            audioGo.AddComponent<BattleAudioController>().Bind(director);

            root.AddComponent<BattleParticleVFX>().Bind(director, tableView);

            XRRigFactory.EnsureLighting();
            XRRigFactory.CreateRig(tableCenter, seatedMode, out _);

            director.SetBoss(bossId);
            return director;
        }
    }
}
