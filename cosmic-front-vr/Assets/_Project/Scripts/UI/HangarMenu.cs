using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Network;

namespace CosmicFront.UI
{
    public class HangarMenu : MonoBehaviour
    {
        [SerializeField] private Dropdown teamDropdown;
        [SerializeField] private Dropdown mechDropdown;
        [SerializeField] private Dropdown mapDropdown;
        [SerializeField] private Button startButton;
        [SerializeField] private Button hostButton;
        [SerializeField] private Button joinButton;
        [SerializeField] private InputField addressInput;
        [SerializeField] private Text statusText;
        [SerializeField] private Text controlsHint;

        private void Awake()
        {
            if (startButton != null)
            {
                startButton.onClick.AddListener(OnStartClicked);
            }

            if (hostButton != null)
            {
                hostButton.onClick.AddListener(OnHostClicked);
            }

            if (joinButton != null)
            {
                joinButton.onClick.AddListener(OnJoinClicked);
            }

            PopulateDropdowns();
            NetworkBootstrap.StatusChanged += OnNetworkStatus;
        }

        private void OnDestroy()
        {
            NetworkBootstrap.StatusChanged -= OnNetworkStatus;
        }

        private void Start()
        {
            if (GameManager.Instance == null)
            {
                var go = new GameObject("GameManager");
                go.AddComponent<GameManager>();
            }

            if (addressInput != null && string.IsNullOrWhiteSpace(addressInput.text))
            {
                addressInput.text = NetworkSessionConfig.DefaultAddress;
            }

            UpdateStatus("单机 / Host / Join Dedicated 或局域网");
            UpdateControlsHint();
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter))
            {
                OnStartClicked();
            }
        }

        private void PopulateDropdowns()
        {
            if (teamDropdown != null)
            {
                teamDropdown.ClearOptions();
                teamDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "地球联合军 (Terran Union)",
                    "轨道联盟 (Orbital League)"
                });
            }

            if (mechDropdown != null)
            {
                mechDropdown.ClearOptions();
                mechDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "轻型 — 迅影 Kestrel",
                    "重型 — 重盾 Bastion"
                });
            }

            if (mapDropdown != null)
            {
                mapDropdown.ClearOptions();
                mapDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "环带外壁 — Station Rim",
                    "碎屑航道 — Debris Lane"
                });
            }
        }

        private void OnStartClicked()
        {
            if (!ApplyLoadout())
            {
                return;
            }

            GameManager.Instance.StartSinglePlayerMission();
        }

        private void OnHostClicked()
        {
            if (!ApplyLoadout())
            {
                return;
            }

            UpdateStatus("正在启动 Host...");
            GameManager.Instance.StartMultiplayerHost();
        }

        private void OnJoinClicked()
        {
            if (!ApplyLoadout())
            {
                return;
            }

            var address = addressInput != null ? addressInput.text : NetworkSessionConfig.DefaultAddress;
            UpdateStatus($"正在加入 {address}...");
            GameManager.Instance.StartMultiplayerClient(address);
        }

        private bool ApplyLoadout()
        {
            if (GameManager.Instance == null)
            {
                return false;
            }

            var team = TeamId.Terran;
            var mech = MechArchetype.Light;

            if (teamDropdown != null)
            {
                team = teamDropdown.value == 0 ? TeamId.Terran : TeamId.Orbital;
            }

            if (mechDropdown != null)
            {
                mech = mechDropdown.value == 0 ? MechArchetype.Light : MechArchetype.Heavy;
            }

            GameManager.Instance.SelectLoadout(team, mech);

            if (mapDropdown != null && mapDropdown.value == 1)
            {
                GameManager.Instance.SelectBattleScene(GameManager.Instance.GetAsteroidSceneName());
            }
            else
            {
                GameManager.Instance.SelectBattleScene(null);
            }

            return true;
        }

        private void OnNetworkStatus(string message)
        {
            UpdateStatus(message);
        }

        public void UpdateStatus(string message)
        {
            if (statusText != null)
            {
                statusText.text = message;
            }
        }

        private void UpdateControlsHint()
        {
            if (controlsHint == null)
            {
                return;
            }

            controlsHint.text = VRMechInput.IsHeadsetPresent()
                ? "VR: 左摇杆移动 | 右扳机射击 | Dedicated: Join + 服务器IP"
                : "键鼠: WASD | Tab锁定 | 端口7770 | Dedicated: -cosmicServer";
        }
    }
}
