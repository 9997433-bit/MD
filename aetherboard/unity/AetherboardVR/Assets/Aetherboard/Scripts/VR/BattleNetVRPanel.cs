using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Aetherboard.VR
{
    /// <summary>
    /// World-space network panel for VR / Quest — ray-friendly Host IP + connect controls.
    /// </summary>
    public class BattleNetVRPanel : MonoBehaviour
    {
        private BattleNetSession _net;
        private InputField _ipField;
        private Text _statusText;
        private TouchScreenKeyboard _keyboard;

        public void Bind(BattleNetSession net)
        {
            _net = net;
            if (_ipField == null) BuildUi();
            _ipField.onEndEdit.RemoveAllListeners();
            _ipField.onEndEdit.AddListener(_ =>
            {
                _net?.SetHostAddress(_ipField.text);
                RefreshStatus();
            });
            _ipField.text = net.HostAddress;
            RefreshStatus();
        }

        private void Update()
        {
            if (_keyboard == null || !_keyboard.active) return;
            if (_ipField != null) _ipField.text = _keyboard.text;
            if (_keyboard.status == TouchScreenKeyboard.Status.Done)
            {
                ApplyAddress();
                _keyboard = null;
            }
        }

        private void BuildUi()
        {
            EnsureEventSystem();

            var canvas = gameObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.WorldSpace;
            TryAddTrackedDeviceRaycaster(canvas);

            var scaler = gameObject.AddComponent<CanvasScaler>();
            scaler.dynamicPixelsPerUnit = 10f;

            gameObject.AddComponent<GraphicRaycaster>();

            var rect = gameObject.GetComponent<RectTransform>();
            if (rect == null) rect = gameObject.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(420, 300);
            transform.localScale = Vector3.one * 0.0012f;

            var panel = CreatePanel(transform, new Color(0.08f, 0.1f, 0.14f, 0.92f));
            Stretch(panel.GetComponent<RectTransform>());

            var layout = panel.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(16, 16, 16, 16);
            layout.spacing = 8;
            layout.childForceExpandWidth = true;
            layout.childControlHeight = true;
            layout.childForceExpandHeight = false;

            CreateLabel(panel, "<b>联机</b> — Host IP / 传输");
            _ipField = CreateInputField(panel, BattleNetPrefs.LoadHost());
            _statusText = CreateLabel(panel, "—");

            var row1 = CreateRow(panel);
            CreateButton(row1, "Host", () => _net?.SetRole(NetSessionRole.Host));
            CreateButton(row1, "Client", ApplyAndConnect);
            CreateButton(row1, "离线", () => _net?.SetRole(NetSessionRole.Offline));

            var row2 = CreateRow(panel);
            CreateButton(row2, "传输切换", () =>
            {
                _net?.CycleClientTransport();
                RefreshStatus();
            });
            CreateButton(row2, "键盘输入", OpenTouchKeyboard);

            var row3 = CreateRow(panel);
            CreateButton(row3, "P1", () => _net?.SetLocalPlayerId(1));
            CreateButton(row3, "P2", () => _net?.SetLocalPlayerId(2));
            CreateButton(row3, "刷新", RefreshStatus);

            CreateLabel(panel, "<size=11>TCP 8767 · WS 8769 · NGO 7777</size>");
        }

        private void ApplyAndConnect()
        {
            if (_net == null || _ipField == null) return;
            _net.ApplyHostAddressAndConnectAsClient(_ipField.text);
            RefreshStatus();
        }

        private void ApplyAddress()
        {
            if (_net == null || _ipField == null) return;
            _net.SetHostAddress(_ipField.text);
            RefreshStatus();
        }

        private void OpenTouchKeyboard()
        {
            if (_ipField == null) return;
#if UNITY_ANDROID && !UNITY_EDITOR
            _keyboard = TouchScreenKeyboard.Open(
                _ipField.text,
                TouchScreenKeyboardType.NumbersAndPunctuation,
                false,
                false,
                false,
                false,
                "Host IP");
#else
            Debug.Log("[Aetherboard] Touch keyboard available on Quest/Android builds.");
#endif
        }

        private void RefreshStatus()
        {
            if (_statusText == null || _net == null) return;
            _statusText.text =
                $"{_net.Role} · {_net.ClientTransport}\n" +
                $"{_net.ActiveTransport}\n" +
                $"{_net.HostAddress}  P{_net.LocalPlayerId}";
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

        private static Text CreateLabel(Transform parent, string text)
        {
            var go = new GameObject("Label", typeof(RectTransform), typeof(Text));
            go.transform.SetParent(parent, false);
            var label = go.GetComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = 18;
            label.color = Color.white;
            label.supportRichText = true;
            label.text = text;
            var le = go.AddComponent<LayoutElement>();
            le.minHeight = 24;
            return label;
        }

        private static InputField CreateInputField(Transform parent, string initial)
        {
            var root = new GameObject("InputField", typeof(RectTransform), typeof(Image), typeof(InputField));
            root.transform.SetParent(parent, false);
            root.GetComponent<Image>().color = new Color(0.15f, 0.18f, 0.24f, 1f);
            var le = root.AddComponent<LayoutElement>();
            le.minHeight = 36;

            var textGo = new GameObject("Text", typeof(RectTransform), typeof(Text));
            textGo.transform.SetParent(root.transform, false);
            var text = textGo.GetComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = 18;
            text.color = Color.white;
            text.supportRichText = false;
            var textRt = textGo.GetComponent<RectTransform>();
            Stretch(textRt);
            textRt.offsetMin = new Vector2(10, 4);
            textRt.offsetMax = new Vector2(-10, -4);

            var field = root.GetComponent<InputField>();
            field.textComponent = text;
            field.text = initial;
            field.lineType = InputField.LineType.SingleLine;
            return field;
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

        private static Transform CreateRow(Transform parent)
        {
            var go = new GameObject("Row", typeof(RectTransform), typeof(HorizontalLayoutGroup));
            go.transform.SetParent(parent, false);
            var layout = go.GetComponent<HorizontalLayoutGroup>();
            layout.spacing = 8;
            layout.childForceExpandWidth = true;
            layout.childControlWidth = true;
            var le = go.AddComponent<LayoutElement>();
            le.minHeight = 34;
            return go.transform;
        }

        private static void CreateButton(Transform parent, string label, UnityEngine.Events.UnityAction onClick)
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

            var button = go.GetComponent<Button>();
            button.onClick.AddListener(onClick);
        }
    }
}
