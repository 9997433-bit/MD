using UnityEngine;

namespace Aetherboard.VR
{
    public enum CoopMode
    {
        Solo,
        SplitCoop
    }

    /// <summary>
    /// Local 2-player: P1 controls 铁卫+游弦, P2 controls 白愈+黑炎.
    /// </summary>
    public class CoopController : MonoBehaviour
    {
        public CoopMode Mode { get; private set; } = CoopMode.Solo;
        public int ActivePlayer { get; private set; } = 1;

        private static readonly string[] Player1Units = { "knight", "bard" };
        private static readonly string[] Player2Units = { "white_mage", "black_mage" };

        public void ToggleMode()
        {
            Mode = Mode == CoopMode.Solo ? CoopMode.SplitCoop : CoopMode.Solo;
            ActivePlayer = 1;
        }

        public void SwitchActivePlayer()
        {
            if (Mode == CoopMode.Solo) return;
            ActivePlayer = ActivePlayer == 1 ? 2 : 1;
        }

        public void SetNetworkCoop(bool enabled)
        {
            Mode = enabled ? CoopMode.SplitCoop : CoopMode.Solo;
            ActivePlayer = 1;
        }

        public bool CanControlUnit(string unitId)
        {
            if (Mode == CoopMode.Solo) return true;
            var allowed = ActivePlayer == 1 ? Player1Units : Player2Units;
            foreach (var id in allowed)
                if (id == unitId) return true;
            return false;
        }

        public string ActivePlayerLabel => Mode == CoopMode.Solo
            ? "单人"
            : $"P{ActivePlayer} ({(ActivePlayer == 1 ? "铁卫/游弦" : "白愈/黑炎")})";

        public Color GetPlayerTint(int player) =>
            player == 1 ? new Color(0.3f, 0.6f, 1f) : new Color(1f, 0.45f, 0.35f);
    }
}
