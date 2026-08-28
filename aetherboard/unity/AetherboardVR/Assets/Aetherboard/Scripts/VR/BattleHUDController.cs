using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class BattleHUDController : MonoBehaviour
    {
        private BattleDirector _director;
        private CoopController _coop;
        private Vector2 _scroll;
        private string _hostAddressEdit;
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
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("冰灵 (3)", _btnW)) _director.SetBoss("ice");
            if (GUILayout.Button("火灵 (4)", _btnW)) _director.SetBoss("fire");
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

            GUILayout.BeginHorizontal();
            if (GUILayout.Button("导出回放 (F6)", _btnW))
            {
                GUIUtility.systemCopyBuffer = _director.ExportCommandLogJson();
                _director.SaveCommandLogToFile();
            }
            if (GUILayout.Button("回放 (F7)", _btnW)) _director.LoadAndReplayFromFile();
            GUILayout.EndHorizontal();
            GUILayout.Label($"命令记录: {_director.CommandLog.Commands.Count} 条", RichLabel());

            var net = FindObjectOfType<BattleNetSession>();
            if (net != null)
            {
                if (string.IsNullOrEmpty(_hostAddressEdit))
                    _hostAddressEdit = net.HostAddress;

                GUILayout.BeginHorizontal();
                if (GUILayout.Button("离线", _btnW)) net.SetRole(NetSessionRole.Offline);
                if (GUILayout.Button("Host", _btnW)) net.SetRole(NetSessionRole.Host);
                if (GUILayout.Button("Client", _btnW)) net.ApplyHostAddressAndConnectAsClient(_hostAddressEdit);
                GUILayout.EndHorizontal();

                GUILayout.BeginHorizontal();
                GUILayout.Label("Host IP:", GUILayout.Width(56));
                _hostAddressEdit = GUILayout.TextField(_hostAddressEdit, GUILayout.Width(150));
                if (GUILayout.Button("保存", GUILayout.Width(48)))
                    net.SetHostAddress(_hostAddressEdit);
                GUILayout.EndHorizontal();

                GUILayout.Label(
                    $"网络: {net.Role}  {net.ActiveTransport}  P{net.LocalPlayerId}",
                    RichLabel());
                GUILayout.Label(
                    $"地址 {net.HostAddress}  |  TCP {net.HostPort}  WS {net.HostWsPort}  NGO {net.HostNgoPort}",
                    RichLabel());
                GUILayout.BeginHorizontal();
                if (GUILayout.Button($"传输: {net.ClientTransport}", _btnW))
                    net.CycleClientTransport();
                GUILayout.EndHorizontal();
                if (_coop != null && _coop.Mode == CoopMode.SplitCoop)
                {
                    GUILayout.BeginHorizontal();
                    if (GUILayout.Button("网络 P1", _btnW)) net.SetLocalPlayerId(1);
                    if (GUILayout.Button("网络 P2", _btnW)) net.SetLocalPlayerId(2);
                    GUILayout.EndHorizontal();
                }
            }

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

            GUILayout.Label("<size=10>LMB移动 | RMB技能 | C双人 Tab切玩家 | H/N联机 B传输 | F5/F9存读档 | F6/F7回放 | E/A/1/2/3/4</size>", RichLabel());
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
            TelegraphKind.IceLance => "冰枪",
            TelegraphKind.FrozenGround => "霜冻",
            TelegraphKind.IceRing => "冰环",
            TelegraphKind.Blizzard => "暴雪",
            TelegraphKind.FlameBreath => "火息",
            TelegraphKind.Meteor => "陨石",
            TelegraphKind.HeatLink => "灼热连结",
            TelegraphKind.Eruption => "喷发",
            _ => "—"
        };
    }
}
