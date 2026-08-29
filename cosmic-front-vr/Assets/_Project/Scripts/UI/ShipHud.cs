using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Ship;

namespace CosmicFront.UI
{
    public class ShipHud : MonoBehaviour
    {
        [SerializeField] private Text roleText;
        [SerializeField] private Text shipStatusText;
        [SerializeField] private Slider shipHealthBar;
        [SerializeField] private Slider shipShieldBar;
        [SerializeField] private Slider abilityBar;

        private ShipCrewMember _crew;

        private void Update()
        {
            if (_crew == null)
            {
                _crew = FindObjectOfType<ShipCrewMember>();
            }

            if (_crew == null || !_crew.IsBoarded || _crew.CurrentShip == null)
            {
                SetVisible(false);
                return;
            }

            SetVisible(true);
            var ship = _crew.CurrentShip;
            if (roleText != null)
            {
                roleText.text = $"席位: {_crew.CurrentRole} — {ship.DisplayName}";
            }

            if (shipStatusText != null)
            {
                shipStatusText.text = $"航速 {ship.Movement.CurrentSpeed:F0} m/s | X退出 L弹射 V舰长技能";
            }

            if (shipHealthBar != null && ship.Health != null)
            {
                shipHealthBar.value = ship.Health.MaxHealth > 0f
                    ? ship.Health.CurrentHealth / ship.Health.MaxHealth
                    : 0f;
            }

            if (shipShieldBar != null && ship.Health != null)
            {
                shipShieldBar.value = ship.Health.MaxShield > 0f
                    ? ship.Health.CurrentShield / ship.Health.MaxShield
                    : 0f;
            }

            if (abilityBar != null && ship.Captain != null)
            {
                abilityBar.value = ship.Captain.CooldownNormalized;
            }
        }

        private void SetVisible(bool visible)
        {
            if (roleText != null) roleText.enabled = visible;
            if (shipStatusText != null) shipStatusText.enabled = visible;
            if (shipHealthBar != null) shipHealthBar.gameObject.SetActive(visible);
            if (shipShieldBar != null) shipShieldBar.gameObject.SetActive(visible);
            if (abilityBar != null) abilityBar.gameObject.SetActive(visible);
        }
    }
}
