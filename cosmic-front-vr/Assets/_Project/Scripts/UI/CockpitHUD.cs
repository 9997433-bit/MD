using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.UI
{
    public class CockpitHUD : MonoBehaviour
    {
        [SerializeField] private Slider healthBar;
        [SerializeField] private Slider shieldBar;
        [SerializeField] private Slider boostBar;
        [SerializeField] private Text lockIndicator;
        [SerializeField] private Text speedLabel;
        [SerializeField] private MechController mech;
        [SerializeField] private MechMovement movement;
        [SerializeField] private HealthSystem health;
        [SerializeField] private LockOnSystem lockOn;

        private void Awake()
        {
            if (mech != null)
            {
                Bind(mech);
            }
        }

        public void Bind(MechController target)
        {
            mech = target;
            movement = mech.GetComponent<MechMovement>();
            health = mech.GetComponent<HealthSystem>();
            lockOn = mech.GetComponent<LockOnSystem>();

            if (health != null)
            {
                health.HealthChanged += OnHealthChanged;
                OnHealthChanged(health.CurrentHealth, health.MaxHealth, health.CurrentShield, health.MaxShield);
            }
        }

        private void OnDestroy()
        {
            if (health != null)
            {
                health.HealthChanged -= OnHealthChanged;
            }
        }

        private void Update()
        {
            if (movement != null && boostBar != null)
            {
                boostBar.value = movement.BoostFuelNormalized;
            }

            if (movement != null && speedLabel != null)
            {
                speedLabel.text = $"{movement.CurrentSpeed:F0} m/s";
            }

            if (lockOn != null && lockIndicator != null)
            {
                lockIndicator.text = lockOn.CurrentTarget != null ? "LOCK" : "---";
            }
        }

        private void OnHealthChanged(float hp, float maxHp, float sh, float maxSh)
        {
            if (healthBar != null && maxHp > 0f)
            {
                healthBar.value = hp / maxHp;
            }

            if (shieldBar != null && maxSh > 0f)
            {
                shieldBar.value = sh / maxSh;
            }
        }
    }
}
