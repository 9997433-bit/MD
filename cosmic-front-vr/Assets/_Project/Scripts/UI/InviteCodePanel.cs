using System;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using CosmicFront.Core;
using CosmicFront.Network;
using CosmicFront.Steam;
using UnityEngine;
using UnityEngine.UI;

namespace CosmicFront.UI
{
    /// <summary>
    /// Shows the current Steam invite deep-link and copies it to the system clipboard.
    /// Refreshes after a successful Host start.
    /// </summary>
    public class InviteCodePanel : MonoBehaviour
    {
        [SerializeField] private Text inviteText;
        [SerializeField] private Button copyButton;
        [SerializeField] private Text copyFeedbackText;
        [SerializeField] private string placeholder = "Host 后生成邀请串";

        public string CurrentInvite { get; private set; } = string.Empty;

        private void Awake()
        {
            EnsureUi();

            if (copyButton != null)
            {
                copyButton.onClick.AddListener(CopyInvite);
            }
        }

        private void OnEnable()
        {
            NetworkBootstrap.StatusChanged += OnNetworkStatus;
            if (GameManager.Instance != null)
            {
                GameManager.Instance.PhaseChanged += OnPhaseChanged;
            }
        }

        private void OnDisable()
        {
            NetworkBootstrap.StatusChanged -= OnNetworkStatus;
            if (GameManager.Instance != null)
            {
                GameManager.Instance.PhaseChanged -= OnPhaseChanged;
            }
        }

        private void Start()
        {
            if (NetworkBootstrap.IsServer)
            {
                RefreshInvite();
            }
            else
            {
                ShowPlaceholder();
            }
        }

        public void RefreshInvite()
        {
            EnsureSteamManager();

            var ip = ResolveLanAddress();
            var port = NetworkSessionConfig.Port;
            CurrentInvite = SteamManager.Instance != null
                ? SteamManager.Instance.GetInviteConnectString(ip, port)
                : $"cosmicfront://join?ip={ip}&port={port}";

            if (inviteText != null)
            {
                inviteText.text = CurrentInvite;
            }

            if (copyFeedbackText != null)
            {
                copyFeedbackText.text = "可复制分享给队友";
            }
        }

        public void CopyInvite()
        {
            if (string.IsNullOrEmpty(CurrentInvite))
            {
                RefreshInvite();
            }

            if (string.IsNullOrEmpty(CurrentInvite))
            {
                return;
            }

            GUIUtility.systemCopyBuffer = CurrentInvite;

            if (copyFeedbackText != null)
            {
                copyFeedbackText.text = "已复制到剪贴板";
            }

            Debug.Log($"[InviteCodePanel] Copied: {CurrentInvite}");
        }

        private void OnNetworkStatus(string message)
        {
            if (GameManager.Instance == null ||
                GameManager.Instance.CurrentMatchMode != MatchMode.MultiplayerHost)
            {
                return;
            }

            // Host path raises "网络已连接，载入战场..." after host client connects.
            if (message != null &&
                (message.IndexOf("网络已连接", StringComparison.Ordinal) >= 0 ||
                 NetworkBootstrap.IsServer))
            {
                RefreshInvite();
            }
        }

        private void OnPhaseChanged(GamePhase phase)
        {
            if (phase != GamePhase.Loading && phase != GamePhase.Battle)
            {
                return;
            }

            if (GameManager.Instance != null &&
                GameManager.Instance.CurrentMatchMode == MatchMode.MultiplayerHost)
            {
                RefreshInvite();
            }
        }

        private void ShowPlaceholder()
        {
            CurrentInvite = string.Empty;
            if (inviteText != null)
            {
                inviteText.text = placeholder;
            }
        }

        private void EnsureUi()
        {
            if (inviteText != null && copyButton != null)
            {
                return;
            }

            var parent = transform as RectTransform;
            if (parent == null)
            {
                var canvas = FindObjectOfType<Canvas>();
                if (canvas == null)
                {
                    return;
                }

                transform.SetParent(canvas.transform, false);
                parent = gameObject.GetComponent<RectTransform>() ?? gameObject.AddComponent<RectTransform>();
                parent.anchorMin = new Vector2(0.5f, 0f);
                parent.anchorMax = new Vector2(0.5f, 0f);
                parent.pivot = new Vector2(0.5f, 0f);
                parent.anchoredPosition = new Vector2(0f, 24f);
                parent.sizeDelta = new Vector2(520f, 72f);
            }

            if (inviteText == null)
            {
                inviteText = CreateLabel(parent, "InviteText", placeholder, new Vector2(0f, 18f), 12);
            }

            if (copyFeedbackText == null)
            {
                copyFeedbackText = CreateLabel(parent, "CopyFeedback", "", new Vector2(0f, -4f), 11);
                copyFeedbackText.color = new Color(0.7f, 0.85f, 1f);
            }

            if (copyButton == null)
            {
                copyButton = CreateCopyButton(parent);
            }
        }

        private static Text CreateLabel(Transform parent, string name, string value, Vector2 pos, int fontSize)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.5f, 0.5f);
            rt.anchorMax = new Vector2(0.5f, 0.5f);
            rt.pivot = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(500f, 22f);
            var text = go.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = fontSize;
            text.alignment = TextAnchor.MiddleCenter;
            text.color = Color.white;
            text.text = value;
            text.horizontalOverflow = HorizontalWrapMode.Overflow;
            text.verticalOverflow = VerticalWrapMode.Truncate;
            return text;
        }

        private static Button CreateCopyButton(Transform parent)
        {
            var go = new GameObject("CopyInviteButton", typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = go.GetComponent<RectTransform>();
            rt.anchorMin = new Vector2(0.5f, 0.5f);
            rt.anchorMax = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = new Vector2(0f, -28f);
            rt.sizeDelta = new Vector2(160f, 28f);

            var image = go.AddComponent<Image>();
            image.color = new Color(0.18f, 0.35f, 0.55f, 0.95f);

            var button = go.AddComponent<Button>();
            button.targetGraphic = image;

            var labelGo = new GameObject("Label", typeof(RectTransform));
            labelGo.transform.SetParent(go.transform, false);
            var labelRt = labelGo.GetComponent<RectTransform>();
            labelRt.anchorMin = Vector2.zero;
            labelRt.anchorMax = Vector2.one;
            labelRt.offsetMin = Vector2.zero;
            labelRt.offsetMax = Vector2.zero;
            var label = labelGo.AddComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            label.fontSize = 13;
            label.alignment = TextAnchor.MiddleCenter;
            label.color = Color.white;
            label.text = "复制邀请串";

            return button;
        }

        private static void EnsureSteamManager()
        {
            if (SteamManager.Instance != null)
            {
                return;
            }

            var go = new GameObject("SteamManager");
            go.AddComponent<SteamManager>();
        }

        public static string ResolveLanAddress()
        {
            try
            {
                foreach (var ni in NetworkInterface.GetAllNetworkInterfaces())
                {
                    if (ni.OperationalStatus != OperationalStatus.Up)
                    {
                        continue;
                    }

                    if (ni.NetworkInterfaceType == NetworkInterfaceType.Loopback)
                    {
                        continue;
                    }

                    foreach (var addr in ni.GetIPProperties().UnicastAddresses)
                    {
                        if (addr.Address.AddressFamily != AddressFamily.InterNetwork)
                        {
                            continue;
                        }

                        var s = addr.Address.ToString();
                        if (s.StartsWith("169.254.", StringComparison.Ordinal))
                        {
                            continue;
                        }

                        return s;
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[InviteCodePanel] LAN resolve failed: {e.Message}");
            }

            try
            {
                var host = Dns.GetHostEntry(Dns.GetHostName());
                foreach (var addr in host.AddressList)
                {
                    if (addr.AddressFamily == AddressFamily.InterNetwork)
                    {
                        return addr.ToString();
                    }
                }
            }
            catch
            {
                // ignored
            }

            return NetworkSessionConfig.DefaultAddress;
        }
    }
}
