using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Quest/Android runtime smoke diagnostics — logs device and LAN info for sideload verification.
    /// </summary>
    public class QuestRuntimeDiagnostics : MonoBehaviour
    {
        [SerializeField] private bool logOnStart = true;
        [SerializeField] private float repeatLogIntervalSec;

        private float _nextLogTime;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void AutoAttachOnQuest()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (Object.FindObjectOfType<QuestRuntimeDiagnostics>() != null) return;
            var go = new GameObject("QuestRuntimeDiagnostics");
            go.hideFlags = HideFlags.DontSave;
            go.AddComponent<QuestRuntimeDiagnostics>();
#endif
        }

        private void Start()
        {
            if (logOnStart) LogSnapshot();
        }

        private void Update()
        {
            if (repeatLogIntervalSec <= 0f) return;
            if (Time.unscaledTime < _nextLogTime) return;
            _nextLogTime = Time.unscaledTime + repeatLogIntervalSec;
            LogSnapshot();
        }

        public void LogSnapshot()
        {
            var path = QuestVerificationReport.WriteReportFiles();
            var report = QuestVerificationReport.BuildReport(includeManualChecklist: false);
            Debug.Log($"{report}\n  Report file: {path}\n  Public copy: {QuestVerificationReport.PublicReportPath}");
        }
    }
}
