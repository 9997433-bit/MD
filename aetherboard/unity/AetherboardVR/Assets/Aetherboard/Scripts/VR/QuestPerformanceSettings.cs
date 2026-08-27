using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Applies Quest-friendly frame rate and quality defaults at runtime.
    /// </summary>
    public class QuestPerformanceSettings : MonoBehaviour
    {
        [SerializeField] private int targetFrameRate = 72;
        [SerializeField] private bool disableVsync = true;

        private void Awake()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (disableVsync) QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = targetFrameRate;
            QualitySettings.shadows = ShadowQuality.Disable;
            BattleLightingController.ApplyQuestProfile();
            BattlePostProcessController.ApplyQuestProfile();
#endif
        }
    }
}
