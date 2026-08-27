using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class BattleHUDController : MonoBehaviour
    {
        private BattleDirector _director;
        private CoopController _coop;
        private Vector2 _scroll;
        private readonly GUILayoutOption _btnW = GUILayout.Width(118);

        public void Bind(BattleDirector director, CoopController coop)
        {
            _director = director;
            _coop = coop;
        }

        private void OnGUI()
        {
            if (_director == null) return;
            var state = _director.State;
            var boss = state.Boss;

            GUILayout.BeginArea(new Rect(12, 12, 340, Screen.height - 24), GUI.skin.box);
            GUILayout.Label("<b>Aetherboard</b>", RichLabel());
            GUILayout.Label($"Boss: {boss.Name}  HP {boss.Hp}/{boss.MaxHp}  P{boss.Phase}");
            GUILayout.Label($"回合 {state.Turn}  |  阶段: {PhaseLabel(state.Phase)}");
            if (_coop != null)
                GUILayout.Label($"模式: {_coop.ActivePlayerLabel}", RichLabel());
            GUILayout.Label($"机制: {TelegraphLabel(boss.Telegraph)}");
            if (boss.FuryCastTurns > 0)
                GUILayout.Label($"<color=red>读条剩余 {boss.FuryCastTurns} 回合</color>", RichLabel());

            GUILayout.Space(6);
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("结束阶段 (E)", _btnW)) _director.EndCurrentPhase();
            if (GUILayout.Button("自动一步 (A)", _btnW)) _director.StepAuto();
            GUILayout.EndHorizontal();

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("土灵 (1)", _btnW)) _director.SetBoss("earth");
            if (GUILayout.Button("风灵 (2)", _btnW)) _director.SetBoss("wind");
            GUILayout.EndHorizontal();

            if (_coop != null)
            {
                GUILayout.BeginHorizontal();
                if (GUILayout.Button("双人模式 (C)", _btnW)) { _coop.ToggleMode(); _director.RefreshAllViews(); }
                if (GUILayout.Button("切换玩家 (Tab)", _btnW)) _coop.SwitchActivePlayer();
                GUILayout.EndHorizontal();
            }

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("存档 (F5)", _btnW)) _director.SaveCheckpoint();
            if (GUILayout.Button("读档 (F9)", _btnW)) _director.RestoreLastSnapshot();
            GUILayout.EndHorizontal();

            GUILayout.Space(4);
            GUILayout.Label("<b>小队</b>", RichLabel());
            foreach (var u in state.Party)
            {
                var tag = UnitOwnerTag(u.Id);
                var status = u.Alive ? $"{u.Hp}/{u.MaxHp}" : "倒下";
                GUILayout.Label($"• [{tag}] {u.DisplayName}  {status}");
            }

            GUILayout.Space(4);
            GUILayout.Label("<b>战斗日志</b>", RichLabel());
            _scroll = GUILayout.BeginScrollView(_scroll, GUILayout.Height(150));
            for (var i = Mathf.Max(0, state.Log.Count - 12); i < state.Log.Count; i++)
                GUILayout.Label(state.Log[i]);
            GUILayout.EndScrollView();

            GUILayout.Label("<size=10>LMB移动 | RMB技能 | C双人 Tab切玩家 | F5/F9存读档 | E/A/1/2</size>", RichLabel());
            GUILayout.EndArea();
        }

        private string UnitOwnerTag(string unitId) => unitId is "knight" or "bard" ? "P1" : "P2";

        private static GUIStyle RichLabel() =>
            new(GUI.skin.label) { richText = true };

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
