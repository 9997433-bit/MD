using UnityEngine;

namespace CosmicFront.Player
{
    /// <summary>
    /// Runtime comfort toggles: Snap/Smooth turn and vignette intensity.
    /// Press F1 to cycle presets (editor / desktop fallback friendly).
    /// </summary>
    public class VRComfortMenu : MonoBehaviour
    {
        [SerializeField] private KeyCode cycleKey = KeyCode.F1;
        [SerializeField] private bool showHud = true;

        private static readonly ComfortPreset[] Presets =
        {
            new ComfortPreset("Snap / 强暗角", true, 0.45f, false),
            new ComfortPreset("Snap / 中暗角", true, 0.35f, false),
            new ComfortPreset("Smooth / 中暗角", false, 0.35f, false),
            new ComfortPreset("Smooth / 弱暗角", false, 0.2f, true),
            new ComfortPreset("Smooth / 无暗角", false, 0f, true),
        };

        private int _presetIndex;
        private string _status = "Comfort: Snap / 中暗角";

        private struct ComfortPreset
        {
            public readonly string Label;
            public readonly bool SnapTurn;
            public readonly float VignetteIntensity;
            public readonly bool DisableStrafe;

            public ComfortPreset(string label, bool snapTurn, float vignetteIntensity, bool disableStrafe)
            {
                Label = label;
                SnapTurn = snapTurn;
                VignetteIntensity = vignetteIntensity;
                DisableStrafe = disableStrafe;
            }
        }

        private void Start()
        {
            SyncIndexFromSettings();
            ApplyPreset(_presetIndex, announce: false);
        }

        private void Update()
        {
            if (Input.GetKeyDown(cycleKey))
            {
                CyclePreset();
            }
        }

        public void CyclePreset()
        {
            _presetIndex = (_presetIndex + 1) % Presets.Length;
            ApplyPreset(_presetIndex, announce: true);
        }

        public void ToggleSnapSmooth()
        {
            var comfort = VRComfortSettings.Instance;
            if (comfort == null)
            {
                return;
            }

            comfort.SnapTurnEnabled = !comfort.SnapTurnEnabled;
            _status = comfort.SnapTurnEnabled
                ? "Comfort: Snap Turn"
                : "Comfort: Smooth Turn (Mech 右摇杆)";
            SyncIndexFromSettings();
            Debug.Log(_status);
        }

        public void SetVignetteIntensity(float intensity)
        {
            var comfort = VRComfortSettings.Instance;
            if (comfort == null)
            {
                return;
            }

            comfort.VignetteIntensity = intensity;
            comfort.VignetteOnBoost = intensity > 0.01f;
            _status = $"Comfort: 暗角 {comfort.VignetteIntensity:0.00}";
            Debug.Log(_status);
        }

        private void ApplyPreset(int index, bool announce)
        {
            var comfort = VRComfortSettings.Instance;
            if (comfort == null)
            {
                return;
            }

            var preset = Presets[Mathf.Clamp(index, 0, Presets.Length - 1)];
            comfort.SnapTurnEnabled = preset.SnapTurn;
            comfort.VignetteIntensity = preset.VignetteIntensity;
            comfort.VignetteOnBoost = preset.VignetteIntensity > 0.01f;
            comfort.DisableStrafeOption = preset.DisableStrafe;
            _status = $"Comfort: {preset.Label}";

            if (announce)
            {
                Debug.Log($"{_status} (F1 循环)");
            }
        }

        private void SyncIndexFromSettings()
        {
            var comfort = VRComfortSettings.Instance;
            if (comfort == null)
            {
                return;
            }

            for (var i = 0; i < Presets.Length; i++)
            {
                var p = Presets[i];
                if (p.SnapTurn == comfort.SnapTurnEnabled
                    && Mathf.Abs(p.VignetteIntensity - comfort.VignetteIntensity) < 0.05f)
                {
                    _presetIndex = i;
                    return;
                }
            }
        }

        private void OnGUI()
        {
            if (!showHud)
            {
                return;
            }

            var style = new GUIStyle(GUI.skin.label)
            {
                fontSize = 14,
                normal = { textColor = Color.white }
            };
            GUI.Label(new Rect(12f, 12f, 480f, 24f), $"{_status}  [{cycleKey} 循环]", style);
        }
    }
}
