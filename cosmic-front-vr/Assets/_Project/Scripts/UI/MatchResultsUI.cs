using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;

namespace CosmicFront.UI
{
    public class MatchResultsUI : MonoBehaviour
    {
        [SerializeField] private GameObject panel;
        [SerializeField] private Text killsText;
        [SerializeField] private Text deathsText;
        [SerializeField] private Button returnButton;

        private void Awake()
        {
            if (returnButton != null)
            {
                returnButton.onClick.AddListener(OnReturn);
            }

            if (GameManager.Instance != null)
            {
                GameManager.Instance.MatchEnded += ShowResults;
                GameManager.Instance.PhaseChanged += OnPhaseChanged;
            }
        }

        private void OnDestroy()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.MatchEnded -= ShowResults;
                GameManager.Instance.PhaseChanged -= OnPhaseChanged;
            }
        }

        private void OnPhaseChanged(GamePhase phase)
        {
            if (panel != null)
            {
                panel.SetActive(phase == GamePhase.Results);
            }
        }

        private void ShowResults()
        {
            if (GameManager.Instance == null)
            {
                return;
            }

            if (killsText != null)
            {
                killsText.text = $"击坠: {GameManager.Instance.PlayerKills}";
            }

            if (deathsText != null)
            {
                deathsText.text = $"被击坠: {GameManager.Instance.PlayerDeaths}";
            }
        }

        private void OnReturn()
        {
            GameManager.Instance?.ReturnToHangar();
        }
    }
}
