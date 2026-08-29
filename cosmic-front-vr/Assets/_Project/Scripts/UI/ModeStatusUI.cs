using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Modes;
using CosmicFront.Network;

namespace CosmicFront.UI
{
    /// <summary>
    /// Extends scoreboard with mode-specific status (escort / capture).
    /// </summary>
    public class ModeStatusUI : MonoBehaviour
    {
        [SerializeField] private Text modeStatusText;

        private EscortFlagshipMode _escort;
        private CapturePointsMode _capture;

        private void Update()
        {
            if (modeStatusText == null || GameManager.Instance == null)
            {
                return;
            }

            switch (GameManager.Instance.SelectedGameMode)
            {
                case GameModeType.EscortFlagship:
                    if (_escort == null)
                    {
                        _escort = FindObjectOfType<EscortFlagshipMode>();
                    }

                    modeStatusText.text = _escort != null
                        ? _escort.BuildStatusText()
                        : "护送模式载入中...";
                    break;

                case GameModeType.CapturePoints:
                    if (_capture == null)
                    {
                        _capture = FindObjectOfType<CapturePointsMode>();
                    }

                    modeStatusText.text = _capture != null
                        ? _capture.BuildStatusText()
                        : "据点模式载入中...";
                    break;

                default:
                    if (NetworkScoreManager.Instance != null)
                    {
                        modeStatusText.text = "模式: 团队死斗";
                    }
                    else if (GameManager.Instance.Phase == GamePhase.Battle)
                    {
                        modeStatusText.text = "模式: 团队死斗 (单机)";
                    }

                    break;
            }
        }
    }
}
