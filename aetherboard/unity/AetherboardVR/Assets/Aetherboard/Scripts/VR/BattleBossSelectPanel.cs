using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// World-space boss picker for VR / Quest — no keyboard required.
    /// </summary>
    public class BattleBossSelectPanel : MonoBehaviour
    {
        private BattleDirector _director;
        private Text _statusText;

        public void Bind(BattleDirector director)
        {
            _director = director;
            if (_statusText == null) BuildUi();
            RefreshStatus();
            _director.OnBossChanged.AddListener(OnBossChangedHandler);
        }

        private void OnDestroy()
        {
            if (_director != null)
                _director.OnBossChanged.RemoveListener(OnBossChangedHandler);
        }

        private void OnBossChangedHandler(string _) => RefreshStatus();

        private void SelectBoss(string bossId)
        {
            _director?.SetBoss(bossId);
            RefreshStatus();
            VRHapticsUtility.PulseLight();
        }

        private void RefreshStatus()
        {
            if (_statusText == null || _director == null) return;
            var id = _director.Engine.BossId;
            var profile = BossRegistry.Get(id);
            _statusText.text = id switch
            {
                "wind" => $"<b>{profile.Create().Name}</b>\n{BossRegistry.MechanicSummary(id)}",
                "ice" => $"<b>{profile.Create().Name}</b>\n{BossRegistry.MechanicSummary(id)}",
                "fire" => $"<b>{profile.Create().Name}</b>\n{BossRegistry.MechanicSummary(id)}",
                _ => $"<b>{profile.Create().Name}</b>\n{BossRegistry.MechanicSummary(id)}"
            };
        }

        private void BuildUi()
        {
            EnsureEventSystem();

            var canvas = gameObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.WorldSpace;
            TryAddTrackedDeviceRaycaster(canvas);

            gameObject.AddComponent<CanvasScaler>().dynamicPixelsPerUnit = 10f;
            gameObject.AddComponent<GraphicRaycaster>();

            var rect = gameObject.GetComponent<RectTransform>() ?? gameObject.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(420, 340);
            transform.localScale = Vector3.one * 0.0012f;

            var panel = CreatePanel(transform, new Color(0.08f, 0.1f, 0.14f, 0.92f));
            Stretch(panel);

            var layout = panel.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(14, 14, 14, 14);
            layout.spacing = 8;
            layout.childForceExpandWidth = true;
            layout.childControlHeight = true;
            layout.childForceExpandHeight = false;

            CreateLabel(panel, "<b>选择 Boss</b>");
            _statusText = CreateLabel(panel, "—");

            var row = CreateRow(panel);
            CreateButton(row, "土灵", () => SelectBoss("earth"), new Color(0.45f, 0.32f, 0.18f));
            CreateButton(row, "风灵", () => SelectBoss("wind"), new Color(0.18f, 0.38f, 0.52f));
            CreateButton(row, "冰灵", () => SelectBoss("ice"), new Color(0.35f, 0.55f, 0.85f));
            CreateButton(row, "火灵", () => SelectBoss("fire"), new Color(0.72f, 0.28f, 0.12f));

            var row2 = CreateRow(panel);
            CreateButton(row2, "下一个 Boss", () =>
            {
                _director?.CycleNextBoss();
                RefreshStatus();
            }, new Color(0.28f, 0.32f, 0.42f));
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
            go.AddComponent<LayoutElement>().minHeight = 28;
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
            go.AddComponent<LayoutElement>().minHeight = 36;
            return go.transform;
        }

        private static void CreateButton(Transform parent, string label, Action onClick, Color color)
        {
            var go = new GameObject(label, typeof(RectTransform), typeof(Image), typeof(Button));
            go.transform.SetParent(parent, false);
            go.GetComponent<Image>().color = color;

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
