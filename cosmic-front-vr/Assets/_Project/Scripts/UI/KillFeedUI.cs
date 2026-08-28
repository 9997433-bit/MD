using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Combat;

namespace CosmicFront.UI
{
    /// <summary>
    /// Left-side scrolling kill feed. Press K to inject a test line.
    /// </summary>
    public class KillFeedUI : MonoBehaviour
    {
        [SerializeField] private Text feedText;
        [SerializeField] private int maxEntries = 8;
        [SerializeField] private float entryLifetime = 10f;
        [SerializeField] private KeyCode testKey = KeyCode.K;

        private readonly List<FeedEntry> _entries = new();
        private readonly StringBuilder _builder = new();
        private int _testIndex;

        private struct FeedEntry
        {
            public string Line;
            public float ExpiresAt;
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void EnsureHudPresent()
        {
            if (FindObjectOfType<KillFeedUI>() != null)
            {
                return;
            }

            var go = new GameObject("KillFeedUI");
            go.AddComponent<KillFeedUI>();
            go.AddComponent<StreakTracker>();
        }

        private void Awake()
        {
            EnsureFeedText();
        }

        private void OnEnable()
        {
            KillFeedEvents.OnKill += HandleKill;
        }

        private void OnDisable()
        {
            KillFeedEvents.OnKill -= HandleKill;
        }

        private void Update()
        {
            if (Input.GetKeyDown(testKey))
            {
                _testIndex++;
                KillFeedEvents.Raise("Player", $"Target_{_testIndex}", "测试");
            }

            var dirty = false;
            var now = Time.unscaledTime;
            for (var i = _entries.Count - 1; i >= 0; i--)
            {
                if (now < _entries[i].ExpiresAt)
                {
                    continue;
                }

                _entries.RemoveAt(i);
                dirty = true;
            }

            if (dirty)
            {
                RefreshText();
            }
        }

        private void HandleKill(string killerName, string victimName, string weapon)
        {
            var line = $"{killerName} [{weapon}] {victimName}";
            _entries.Add(new FeedEntry
            {
                Line = line,
                ExpiresAt = Time.unscaledTime + entryLifetime
            });

            while (_entries.Count > maxEntries)
            {
                _entries.RemoveAt(0);
            }

            RefreshText();
        }

        private void RefreshText()
        {
            if (feedText == null)
            {
                return;
            }

            _builder.Clear();
            for (var i = 0; i < _entries.Count; i++)
            {
                if (i > 0)
                {
                    _builder.Append('\n');
                }

                _builder.Append(_entries[i].Line);
            }

            feedText.text = _builder.ToString();
        }

        private void EnsureFeedText()
        {
            if (feedText != null)
            {
                return;
            }

            var canvas = GetComponentInParent<Canvas>();
            if (canvas == null)
            {
                var canvasGo = new GameObject("KillFeedCanvas");
                canvasGo.transform.SetParent(transform, false);
                canvas = canvasGo.AddComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                canvas.sortingOrder = 40;
                canvasGo.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                canvasGo.AddComponent<GraphicRaycaster>();
            }

            var textGo = new GameObject("KillFeedText");
            textGo.transform.SetParent(canvas.transform, false);
            feedText = textGo.AddComponent<Text>();
            feedText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            feedText.fontSize = 16;
            feedText.color = new Color(1f, 0.92f, 0.75f, 0.95f);
            feedText.alignment = TextAnchor.UpperLeft;
            feedText.horizontalOverflow = HorizontalWrapMode.Overflow;
            feedText.verticalOverflow = VerticalWrapMode.Overflow;
            feedText.raycastTarget = false;

            var rect = feedText.rectTransform;
            rect.anchorMin = new Vector2(0f, 0.35f);
            rect.anchorMax = new Vector2(0f, 0.85f);
            rect.pivot = new Vector2(0f, 1f);
            rect.anchoredPosition = new Vector2(16f, 0f);
            rect.sizeDelta = new Vector2(420f, 0f);
        }
    }
}
