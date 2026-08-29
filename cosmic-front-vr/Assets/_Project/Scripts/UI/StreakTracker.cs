using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Combat;

namespace CosmicFront.UI
{
    /// <summary>
    /// Local kill-streak counter. Shows a banner at 3 / 5 / 7.
    /// </summary>
    public class StreakTracker : MonoBehaviour
    {
        [SerializeField] private Text bannerText;
        [SerializeField] private float bannerDuration = 2.5f;

        private int _streak;
        private float _bannerHideAt;
        private string _localName = "Player";

        private void Awake()
        {
            EnsureBannerText();
            HideBanner();
        }

        private void OnEnable()
        {
            KillFeedEvents.OnKill += HandleKill;
            RefreshLocalName();
        }

        private void OnDisable()
        {
            KillFeedEvents.OnKill -= HandleKill;
        }

        private void Update()
        {
            if (bannerText != null && bannerText.gameObject.activeSelf &&
                Time.unscaledTime >= _bannerHideAt)
            {
                HideBanner();
            }
        }

        private void HandleKill(string killerName, string victimName, string weapon)
        {
            RefreshLocalName();

            if (NamesMatch(victimName, _localName))
            {
                _streak = 0;
                return;
            }

            if (!NamesMatch(killerName, _localName))
            {
                return;
            }

            _streak++;
            TryShowStreakBanner();
        }

        private void TryShowStreakBanner()
        {
            string message = null;
            switch (_streak)
            {
                case 3:
                    message = "三连击!";
                    break;
                case 5:
                    message = "五连击!";
                    break;
                case 7:
                    message = "七连斩!";
                    break;
            }

            if (message == null || bannerText == null)
            {
                return;
            }

            bannerText.text = message;
            bannerText.gameObject.SetActive(true);
            _bannerHideAt = Time.unscaledTime + bannerDuration;
        }

        private void HideBanner()
        {
            if (bannerText != null)
            {
                bannerText.gameObject.SetActive(false);
            }
        }

        private void RefreshLocalName()
        {
            var player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                _localName = KillFeedEvents.ResolveDisplayName(player);
                return;
            }

            _localName = "Player";
        }

        private static bool NamesMatch(string a, string b)
        {
            if (string.IsNullOrEmpty(a) || string.IsNullOrEmpty(b))
            {
                return false;
            }

            return string.Equals(a, b, System.StringComparison.OrdinalIgnoreCase);
        }

        private void EnsureBannerText()
        {
            if (bannerText != null)
            {
                return;
            }

            var canvas = GetComponentInParent<Canvas>();
            if (canvas == null)
            {
                var canvasGo = new GameObject("StreakBannerCanvas");
                canvasGo.transform.SetParent(transform, false);
                canvas = canvasGo.AddComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                canvas.sortingOrder = 50;
                canvasGo.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                canvasGo.AddComponent<GraphicRaycaster>();
            }

            var textGo = new GameObject("StreakBannerText");
            textGo.transform.SetParent(canvas.transform, false);
            bannerText = textGo.AddComponent<Text>();
            bannerText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            bannerText.fontSize = 36;
            bannerText.fontStyle = FontStyle.Bold;
            bannerText.color = new Color(1f, 0.78f, 0.2f, 1f);
            bannerText.alignment = TextAnchor.MiddleCenter;
            bannerText.horizontalOverflow = HorizontalWrapMode.Overflow;
            bannerText.verticalOverflow = VerticalWrapMode.Overflow;
            bannerText.raycastTarget = false;

            var rect = bannerText.rectTransform;
            rect.anchorMin = new Vector2(0.5f, 0.72f);
            rect.anchorMax = new Vector2(0.5f, 0.72f);
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.anchoredPosition = Vector2.zero;
            rect.sizeDelta = new Vector2(640f, 64f);
        }
    }
}
