using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Network;

namespace CosmicFront.UI
{
    public class MatchResultsUI : MonoBehaviour
    {
        [SerializeField] private GameObject panel;
        [SerializeField] private Text killsText;
        [SerializeField] private Text deathsText;
        [SerializeField] private Text teamScoreText;
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

            if (NetworkScoreManager.Instance != null)
            {
                NetworkScoreManager.Instance.MatchEnded += ShowResults;
            }
        }

        private void OnDestroy()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.MatchEnded -= ShowResults;
                GameManager.Instance.PhaseChanged -= OnPhaseChanged;
            }

            if (NetworkScoreManager.Instance != null)
            {
                NetworkScoreManager.Instance.MatchEnded -= ShowResults;
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

            if (teamScoreText != null && NetworkScoreManager.Instance != null)
            {
                teamScoreText.text =
                    $"阵营分 — 地球联合: {NetworkScoreManager.Instance.TerranScore}  |  " +
                    $"轨道联盟: {NetworkScoreManager.Instance.OrbitalScore}";
            }

            if (!string.IsNullOrEmpty(GameManager.Instance.ModeResultMessage) && teamScoreText != null)
            {
                teamScoreText.text = GameManager.Instance.ModeResultMessage + "\n" + (teamScoreText.text ?? string.Empty);
            }
        }

        private void OnReturn()
        {
            GameManager.Instance?.ReturnToHangar();
        }
    }
}
