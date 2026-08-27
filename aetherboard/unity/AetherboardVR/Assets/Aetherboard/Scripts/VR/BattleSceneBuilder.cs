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
            float tableDistance = 1.1f,
            XRRigSource rigSource = XRRigSource.Auto)
        {
            var tableCenter = new Vector3(0, seatedMode ? 0.75f : 1.0f, tableDistance);

            var root = new GameObject("BattleRoot");
            root.transform.position = tableCenter;

            var director = root.AddComponent<BattleDirector>();
            var tableView = root.AddComponent<BattleTableView>();
            var telegraph = root.AddComponent<TelegraphVFXController>();
            var bossView = root.AddComponent<BossHologramView>();
            var coop = root.AddComponent<CoopController>();
            root.AddComponent<VRBattleBootstrap>();

            var highlighter = root.AddComponent<GridSnapHighlighter>();

            tableView.SetCoop(coop);
            tableView.Build(root.transform, director, highlighter, coop);
            telegraph.InitializeProcedural(tableView);
            bossView.InitializeProcedural(root.transform);

            var skillRing = root.AddComponent<SkillRingController>();
            skillRing.Initialize(director, tableView, root.transform);

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
            root.AddComponent<BattleNetSession>();
            root.AddComponent<QuestPerformanceSettings>();

            XRRigFactory.EnsureLighting();
            XRRigFactory.CreateRig(tableCenter, seatedMode, out _, rigSource);

            foreach (var piece in tableView.GetComponentsInChildren<PieceToken>(true))
            {
                var grab = piece.GetComponent<PieceXRGrabController>();
                grab?.Setup(piece, director, tableView, coop, highlighter);
            }

            director.SetBoss(bossId);
            return director;
        }
    }
}
