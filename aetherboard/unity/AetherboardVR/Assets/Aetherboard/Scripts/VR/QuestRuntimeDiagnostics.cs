using System.Net;
using System.Net.Sockets;
using System.Text;
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
        private StringBuilder _buffer = new();

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
            _buffer.Clear();
            _buffer.AppendLine("[Aetherboard Quest] Runtime diagnostics");
            _buffer.AppendLine($"  Device: {SystemInfo.deviceModel} / {SystemInfo.operatingSystem}");
            _buffer.AppendLine($"  GPU: {SystemInfo.graphicsDeviceName}");
            _buffer.AppendLine($"  Target FPS: {Application.targetFrameRate}");
            _buffer.AppendLine($"  XR: {UnityEngine.XR.XRSettings.enabled} ({UnityEngine.XR.XRSettings.loadedDeviceName})");
            _buffer.AppendLine($"  Prefabs: {(BattlePrefabLibrary.HasPrefabs ? "Resources" : "Procedural")}");
            _buffer.AppendLine($"  LAN IP: {TryGetLanIp()}");
            _buffer.AppendLine("  Client: N → B=NetcodeNative | hostAddress=PC LAN IP");
            Debug.Log(_buffer.ToString());
        }

        private static string TryGetLanIp()
        {
            try
            {
                foreach (var address in Dns.GetHostEntry(Dns.GetHostName()).AddressList)
                {
                    if (address.AddressFamily == AddressFamily.InterNetwork && !IPAddress.IsLoopback(address))
                        return address.ToString();
                }
            }
            catch
            {
                // ignore on restricted Android profiles
            }

            return "unknown";
        }
    }
}
