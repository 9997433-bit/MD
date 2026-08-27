using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// IMGUI overlay for phase control — works without Canvas prefab.
    /// </summary>
    public class BattleHUDController : MonoBehaviour
    {
        private BattleDirector _director;
        private DesktopBattleInput _desktop;
        private Vector2 _scroll;
        private readonly GUILayoutOption _btnW = GUILayout.Width(120);

        public void Bind(BattleDirector director)
        {
            _director = director;
            _desktop = director.GetComponent<DesktopBattleInput>();
        }

        private void OnGUI()
        {
            if (_director == null) return;
            var state = _director.State;
            var boss = state.Boss;

            GUILayout.BeginArea(new Rect(12, 12, 320, Screen.height - 24), GUI.skin.box);
            GUILayout.Label("<b>Aetherboard</b>", RichLabel());
            GUILayout.Label($"Boss: {boss.Name}  HP {boss.Hp}/{boss.MaxHp}  P{boss.Phase}");
            GUILayout.Label($"回合 {state.Turn}  |  阶段: {PhaseLabel(state.Phase)}");
            GUILayout.Label($"机制: {TelegraphLabel(boss.Telegraph)}");
            if (boss.FuryCastTurns > 0)
                GUILayout.Label($"<color=red>读条剩余 {boss.FuryCastTurns} 回合</color>", RichLabel());

            GUILayout.Space(6);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("结束阶段 (E)", _btnW)) _director.EndCurrentPhase();
            if (GUILayout.Button("自动一步 (A)", _btnW)) _director.StepAuto();
            GUILayout.EndHorizontal();

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("土灵 Boss (1)", _btnW)) _director.SetBoss("earth");
            if (GUILayout.Button("风灵 Boss (2)", _btnW)) _director.SetBoss("wind");
            GUILayout.EndHorizontal();

            GUILayout.Space(4);
            GUILayout.Label("<b>小队</b>", RichLabel());
            foreach (var u in state.Party)
            {
                var status = u.Alive ? $"{u.Hp}/{u.MaxHp}" : "倒下";
                GUILayout.Label($"• {u.DisplayName}  {status}");
            }

            GUILayout.Space(4);
            GUILayout.Label("<b>战斗日志</b>", RichLabel());
            _scroll = GUILayout.BeginScrollView(_scroll, GUILayout.Height(160));
            for (var i = Mathf.Max(0, state.Log.Count - 12); i < state.Log.Count; i++)
                GUILayout.Label(state.Log[i]);
            GUILayout.EndScrollView();

            GUILayout.Label("<size=10>桌面操作: 点击棋子 → 点击格子移动 | E/A/1/2</size>", RichLabel());
            GUILayout.EndArea();
        }

        private static GUIStyle RichLabel()
        {
            var s = new GUIStyle(GUI.skin.label) { richText = true };
            return s;
        }

        private static string PhaseLabel(BattlePhase phase) => phase switch
        {
            BattlePhase.Warning => "预警",
            BattlePhase.Move => "移动",
            BattlePhase.Action => "GCD",
            BattlePhase.Weave => "oGCD",
            BattlePhase.Resolve => "结算",
            BattlePhase.Victory => "胜利",
            BattlePhase.Defeat => "失败",
            _ => phase.ToString()
        };

        private static string TelegraphLabel(TelegraphKind t) => t switch
        {
            TelegraphKind.Slam => "重击",
            TelegraphKind.Earthquake => "地震",
            TelegraphKind.Shrink => "缩圈",
            TelegraphKind.EarthenFury => "土神之怒",
            TelegraphKind.Gale => "风刃",
            TelegraphKind.Spread => "分散",
            TelegraphKind.Stack => "集合",
            TelegraphKind.Cyclone => "旋风",
            _ => "—"
        };
    }
}
