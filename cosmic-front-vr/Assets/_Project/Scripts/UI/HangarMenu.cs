using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.UI
{
    public class HangarMenu : MonoBehaviour
    {
        [SerializeField] private Dropdown teamDropdown;
        [SerializeField] private Dropdown mechDropdown;
        [SerializeField] private Button startButton;
        [SerializeField] private Text statusText;
        [SerializeField] private Text controlsHint;

        private void Awake()
        {
            if (startButton != null)
            {
                startButton.onClick.AddListener(OnStartClicked);
            }

            PopulateDropdowns();
        }

        private void Start()
        {
            if (GameManager.Instance == null)
            {
                var go = new GameObject("GameManager");
                go.AddComponent<GameManager>();
            }

            UpdateStatus("选择阵营与机甲，开始单机任务");
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
        }

        private void OnStartClicked()
        {
            if (GameManager.Instance == null)
            {
                return;
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
            GameManager.Instance.StartSinglePlayerMission();
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
                ? "VR: 左摇杆移动 | 右摇杆转向 | 右扳机射击 | 左扳机导弹 | 左Grip锁定 | Enter开始"
                : "键鼠: WASD移动 | Tab锁定 | 鼠标射击 | Enter开始";
        }
    }
}
