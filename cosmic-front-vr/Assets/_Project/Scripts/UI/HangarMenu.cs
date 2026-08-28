using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Network;
using CosmicFront.Steam;

namespace CosmicFront.UI
{
    public class HangarMenu : MonoBehaviour
    {
        [SerializeField] private Dropdown teamDropdown;
        [SerializeField] private Dropdown mechDropdown;
        [SerializeField] private Dropdown mapDropdown;
        [SerializeField] private Dropdown spawnDropdown;
        [SerializeField] private Dropdown modeDropdown;
        [SerializeField] private Button startButton;
        [SerializeField] private Button hostButton;
        [SerializeField] private Button joinButton;
        [SerializeField] private InputField addressInput;
        [SerializeField] private Text statusText;
        [SerializeField] private Text controlsHint;
        [SerializeField] private Text steamStatusText;

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

            if (SteamManager.Instance == null)
            {
                var steamGo = new GameObject("SteamManager");
                steamGo.AddComponent<SteamManager>();
            }

            if (addressInput != null && string.IsNullOrWhiteSpace(addressInput.text))
            {
                addressInput.text = NetworkSessionConfig.DefaultAddress;
            }

            UpdateStatus("选择模式 / 地图 / 生成方式后开始");
            UpdateControlsHint();
            UpdateSteamStatus();
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
                    "轨道联盟 (Orbital League)",
                    "维和舰队 (Neutral Force)"
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

            if (spawnDropdown != null)
            {
                spawnDropdown.ClearOptions();
                spawnDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "机甲出击",
                    "战舰 — 舵手",
                    "战舰 — 炮手",
                    "战舰 — 舰长"
                });
            }

            if (modeDropdown != null)
            {
                modeDropdown.ClearOptions();
                modeDropdown.AddOptions(new System.Collections.Generic.List<string>
                {
                    "团队死斗 TDM",
                    "护送旗舰 Escort",
                    "据点争夺 Domination"
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
                switch (teamDropdown.value)
                {
                    case 1:
                        team = TeamId.Orbital;
                        break;
                    case 2:
                        team = TeamId.Neutral;
                        break;
                    default:
                        team = TeamId.Terran;
                        break;
                }
            }

            if (mechDropdown != null)
            {
                mech = mechDropdown.value == 0 ? MechArchetype.Light : MechArchetype.Heavy;
            }

            GameManager.Instance.SelectLoadout(team, mech);

            if (spawnDropdown != null)
            {
                GameManager.Instance.SelectSpawnPreference((SpawnPreference)spawnDropdown.value);
            }
            else
            {
                GameManager.Instance.SelectSpawnPreference(SpawnPreference.Mech);
            }

            if (modeDropdown != null)
            {
                GameManager.Instance.SelectGameMode((GameModeType)modeDropdown.value);
            }
            else
            {
                GameManager.Instance.SelectGameMode(GameModeType.TeamDeathmatch);
            }

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
                ? "VR: 机甲/战舰 | Escort 护旗 | Domination 占点"
                : "键鼠: WASD | B登舰 | 模式: TDM / Escort / Domination";
        }

        private void UpdateSteamStatus()
        {
            if (steamStatusText == null || SteamManager.Instance == null)
            {
                return;
            }

            steamStatusText.text = SteamManager.Instance.IsOfflineFallback
                ? $"Steam: 离线 ({SteamManager.Instance.PersonaName})"
                : $"Steam: {SteamManager.Instance.PersonaName}";
        }
    }
}
