using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace Aetherboard.VR
{
    /// <summary>
    /// Dismissible VR controls cheat sheet — shown once until player closes it.
    /// </summary>
    public class BattleControlsHint : MonoBehaviour
    {
        public const string PrefsKey = "aetherboard_controls_hint_dismissed";

        private Canvas _canvas;

        private void Start()
        {
            if (PlayerPrefs.GetInt(PrefsKey, 0) == 1)
            {
                enabled = false;
                return;
            }

            BuildUi();
        }

        private void Dismiss()
        {
            PlayerPrefs.SetInt(PrefsKey, 1);
            PlayerPrefs.Save();
            if (_canvas != null) _canvas.gameObject.SetActive(false);
            enabled = false;
        }

        public static void ResetDismissedFlag()
        {
            PlayerPrefs.DeleteKey(PrefsKey);
            PlayerPrefs.Save();
        }

        private void BuildUi()
        {
            if (FindObjectOfType<EventSystem>() == null)
            {
                var es = new GameObject("EventSystem");
                es.AddComponent<EventSystem>();
                es.AddComponent<StandaloneInputModule>();
            }

            _canvas = gameObject.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.WorldSpace;

            var raycasterType = System.Type.GetType(
                "UnityEngine.XR.Interaction.Toolkit.UI.TrackedDeviceGraphicRaycaster, Unity.XR.Interaction.Toolkit");
            if (raycasterType != null)
                gameObject.AddComponent(raycasterType);

            gameObject.AddComponent<CanvasScaler>().dynamicPixelsPerUnit = 10f;
            gameObject.AddComponent<GraphicRaycaster>();

            var rect = gameObject.GetComponent<RectTransform>() ?? gameObject.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(400, 280);
            transform.localScale = Vector3.one * 0.0011f;
            transform.localPosition = new Vector3(-0.52f, 0.42f, -0.15f);
            transform.localRotation = Quaternion.Euler(0f, 24f, 0f);

            var panelGo = new GameObject("Panel", typeof(RectTransform), typeof(Image));
            panelGo.transform.SetParent(transform, false);
            panelGo.GetComponent<Image>().color = new Color(0.05f, 0.07f, 0.1f, 0.9f);
            var panel = panelGo.GetComponent<RectTransform>();
            panel.anchorMin = Vector2.zero;
            panel.anchorMax = Vector2.one;
            panel.offsetMin = Vector2.zero;
            panel.offsetMax = Vector2.zero;

            var layout = panelGo.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(14, 14, 14, 14);
            layout.spacing = 6;
            layout.childForceExpandWidth = true;

            AddLabel(panelGo.transform, "<b>操作提示</b>", 20);
            AddLabel(panelGo.transform,
                "Grip — 抓取棋子 / 打开技能环\n" +
                "扳机 — 选中 / 确认技能\n" +
                "A — 结束阶段  |  B — 自动一步\n" +
                "左侧 — 土灵/风灵/冰灵/火灵\n" +
                "右侧 — 联机", 15);

            var btnGo = new GameObject("Dismiss", typeof(RectTransform), typeof(Image), typeof(Button));
            btnGo.transform.SetParent(panelGo.transform, false);
            btnGo.GetComponent<Image>().color = new Color(0.22f, 0.32f, 0.48f, 1f);
            btnGo.GetComponent<Button>().onClick.AddListener(Dismiss);
            var le = btnGo.AddComponent<LayoutElement>();
            le.minHeight = 32;
            AddLabel(btnGo.transform, "知道了", 16).alignment = TextAnchor.MiddleCenter;
        }

        private static Text AddLabel(Transform parent, string text, int size)
        {
            var go = new GameObject("Label", typeof(RectTransform), typeof(Text));
            go.transform.SetParent(parent, false);
            var label = go.GetComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = size;
            label.color = Color.white;
            label.supportRichText = true;
            label.text = text;
            return label;
        }
    }
}
