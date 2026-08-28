using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Network;

namespace CosmicFront.UI
{
    public class MatchScoreboardUI : MonoBehaviour
    {
        [SerializeField] private Text scoreboardText;

        private void OnEnable()
        {
            if (NetworkScoreManager.Instance != null)
            {
                NetworkScoreManager.Instance.ScoresChanged += Refresh;
                Refresh();
            }
        }

        private void OnDisable()
        {
            if (NetworkScoreManager.Instance != null)
            {
                NetworkScoreManager.Instance.ScoresChanged -= Refresh;
            }
        }

        private void Update()
        {
            if (GameManager.Instance != null && !GameManager.Instance.IsMultiplayer)
            {
                RefreshSinglePlayer();
            }
        }

        private void Refresh()
        {
            if (scoreboardText == null || NetworkScoreManager.Instance == null)
            {
                return;
            }

            scoreboardText.text = NetworkScoreManager.Instance.BuildScoreboardText();
        }

        private void RefreshSinglePlayer()
        {
            if (scoreboardText == null || GameManager.Instance == null)
            {
                return;
            }

            scoreboardText.text =
                $"SP  Time {Mathf.CeilToInt(GameManager.Instance.MatchTimeRemaining)}s\n" +
                $"K {GameManager.Instance.PlayerKills}  D {GameManager.Instance.PlayerDeaths}";
        }
    }
}
