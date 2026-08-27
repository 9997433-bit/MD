using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;

namespace CosmicFront.UI
{
    public class HangarMenu : MonoBehaviour
    {
        [SerializeField] private Dropdown teamDropdown;
        [SerializeField] private Dropdown mechDropdown;
        [SerializeField] private Button startButton;
        [SerializeField] private Text statusText;

        private void Awake()
        {
            if (startButton != null)
            {
                startButton.onClick.AddListener(OnStartClicked);
            }
        }

        private void Start()
        {
            if (GameManager.Instance == null)
            {
                var go = new GameObject("GameManager");
                go.AddComponent<GameManager>();
            }

            UpdateStatus("选择阵营与机甲，开始单机任务");
        }

        private void OnStartClicked()
        {
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
    }
}
