using System;
using System.Text;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// World-space battle result summary — victory/defeat stats and rematch actions.
    /// </summary>
    public class BattleResultOverlay : MonoBehaviour
    {
        private BattleDirector _director;
        private Text _titleText;
        private Text _messageText;
        private Text _statsText;
        private Canvas _canvas;

        public void Bind(BattleDirector director)
        {
            _director = director;
            if (_canvas == null) BuildUi();
            Hide();

            _director.OnBattleEnded.AddListener(ShowResult);
            _director.OnPhaseChanged.AddListener(OnPhaseChanged);
        }

        private void OnDestroy()
        {
            if (_director == null) return;
            _director.OnBattleEnded.RemoveListener(ShowResult);
            _director.OnPhaseChanged.RemoveListener(OnPhaseChanged);
        }

        private void OnPhaseChanged(BattlePhase phase)
        {
            if (phase is BattlePhase.Victory or BattlePhase.Defeat)
                ShowResult();
            else if (_canvas != null)
                Hide();
        }

        private void ShowResult()
        {
            if (_director == null || _canvas == null) return;
            var state = _director.State;
            if (state.Phase != BattlePhase.Victory && state.Phase != BattlePhase.Defeat) return;

            var win = state.Phase == BattlePhase.Victory;
            var profile = BossRegistry.Get(_director.Engine.BossId);

            _titleText.text = win ? "<color=#88FFAA>胜利</color>" : "<color=#FF8866>失败</color>";
            _messageText.text = win ? profile.VictoryMessage : "全队阵亡，战斗失败。";
            _statsText.text = BuildStatsBlock(state);

            _canvas.gameObject.SetActive(true);
            FaceCamera();

            if (win) VRHapticsUtility.PulseStrong();
            else VRHapticsUtility.PulseReject();
        }

        private static string BuildStatsBlock(BattleState state)
        {
            var sb = new StringBuilder(256);
            sb.AppendLine($"Boss: {state.Boss.Name}  |  回合 {state.Turn}");
            sb.AppendLine($"Boss HP: {state.Boss.Hp}/{state.Boss.MaxHp}  Phase {state.Boss.Phase}");
            sb.AppendLine("— 小队 —");
            foreach (var unit in state.Party)
            {
                var status = unit.Alive ? $"{unit.Hp}/{unit.MaxHp}" : "倒下";
                sb.AppendLine($"• {unit.DisplayName}  {status}");
            }
            return sb.ToString().TrimEnd();
        }

        private void Hide() => _canvas?.gameObject.SetActive(false);

        private void RestartSameBoss()
        {
            if (_director == null) return;
            _director.SetBoss(_director.Engine.BossId);
            Hide();
            VRHapticsUtility.PulseLight();
        }

        private void SwitchBoss(string bossId)
        {
            _director?.SetBoss(bossId);
            Hide();
            VRHapticsUtility.PulseLight();
        }

        private void BuildUi()
        {
            EnsureEventSystem();

            _canvas = gameObject.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.WorldSpace;
            TryAddTrackedDeviceRaycaster(_canvas);

            var scaler = gameObject.AddComponent<CanvasScaler>();
            scaler.dynamicPixelsPerUnit = 10f;
            gameObject.AddComponent<GraphicRaycaster>();

            var rect = GetComponent<RectTransform>();
            if (rect == null) rect = gameObject.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(460, 340);
            transform.localScale = Vector3.one * 0.0012f;
            transform.localPosition = new Vector3(0f, 0.48f, 0.22f);

            var panel = CreatePanel(transform, new Color(0.06f, 0.08f, 0.12f, 0.94f));
            Stretch(panel);

            var layout = panel.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(18, 18, 18, 18);
            layout.spacing = 10;
            layout.childForceExpandWidth = true;
            layout.childControlHeight = true;
            layout.childForceExpandHeight = false;

            _titleText = CreateLabel(panel, "<b>战斗结束</b>", 28);
            _messageText = CreateLabel(panel, "—", 20);
            _statsText = CreateLabel(panel, "", 16);
            _statsText.alignment = TextAnchor.UpperLeft;

            var row = CreateRow(panel);
            CreateButton(row, "再战", RestartSameBoss);
            CreateButton(row, "土灵", () => SwitchBoss("earth"));
            CreateButton(row, "风灵", () => SwitchBoss("wind"));
            CreateButton(row, "关闭", Hide);

            gameObject.SetActive(true);
            _canvas.gameObject.SetActive(false);
        }

        private void LateUpdate()
        {
            if (_canvas != null && _canvas.gameObject.activeSelf)
                FaceCamera();
        }

        private void FaceCamera()
        {
            var cam = Camera.main;
            if (cam == null) return;
            transform.rotation = Quaternion.LookRotation(
                transform.position - cam.transform.position,
                Vector3.up);
        }

        private static void EnsureEventSystem()
        {
            if (FindObjectOfType<EventSystem>() != null) return;
            var go = new GameObject("EventSystem");
            go.AddComponent<EventSystem>();
            go.AddComponent<StandaloneInputModule>();
        }

        private static void TryAddTrackedDeviceRaycaster(Canvas canvas)
        {
            var raycasterType = Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.UI.TrackedDeviceGraphicRaycaster, Unity.XR.Interaction.Toolkit");
            if (raycasterType != null)
                canvas.gameObject.AddComponent(raycasterType);
        }

        private static RectTransform CreatePanel(Transform parent, Color color)
        {
            var go = new GameObject("Panel", typeof(RectTransform), typeof(Image));
            go.transform.SetParent(parent, false);
            go.GetComponent<Image>().color = color;
            return go.GetComponent<RectTransform>();
        }

        private static void Stretch(RectTransform rt)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }

        private static Text CreateLabel(Transform parent, string text, int fontSize)
        {
            var go = new GameObject("Label", typeof(RectTransform), typeof(Text));
            go.transform.SetParent(parent, false);
            var label = go.GetComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = fontSize;
            label.color = Color.white;
            label.supportRichText = true;
            label.text = text;
            var le = go.AddComponent<LayoutElement>();
            le.minHeight = fontSize + 8;
            return label;
        }

        private static Transform CreateRow(Transform parent)
        {
            var go = new GameObject("Row", typeof(RectTransform), typeof(HorizontalLayoutGroup));
            go.transform.SetParent(parent, false);
            var layout = go.GetComponent<HorizontalLayoutGroup>();
            layout.spacing = 8;
            layout.childForceExpandWidth = true;
            layout.childControlWidth = true;
            var le = go.AddComponent<LayoutElement>();
            le.minHeight = 36;
            return go.transform;
        }

        private static void CreateButton(Transform parent, string label, Action onClick)
        {
            var go = new GameObject(label, typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);
            go.GetComponent<Image>().color = new Color(0.22f, 0.32f, 0.48f, 1f);

            var textGo = new GameObject("Text", typeof(RectTransform), typeof(Text));
            textGo.transform.SetParent(go.transform, false);
            var text = textGo.GetComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = 16;
            text.color = Color.white;
            text.alignment = TextAnchor.MiddleCenter;
            text.text = label;
            Stretch(textGo.GetComponent<RectTransform>());

            go.GetComponent<Button>().onClick.AddListener(() => onClick?.Invoke());
        }
    }
}
