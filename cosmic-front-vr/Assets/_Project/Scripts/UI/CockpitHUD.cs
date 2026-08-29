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
        [SerializeField] private Slider abilityBar;
        [SerializeField] private Text lockIndicator;
        [SerializeField] private Text speedLabel;
        [SerializeField] private Text modelLabel;
        [SerializeField] private Text abilityLabel;
        [SerializeField] private MechController mech;
        [SerializeField] private MechMovement movement;
        [SerializeField] private HealthSystem health;
        [SerializeField] private LockOnSystem lockOn;
        [SerializeField] private MechSpecialAbility ability;

        private void Awake()
        {
            if (mech != null)
            {
                Bind(mech);
            }
        }

        public void Bind(MechController target)
        {
            if (health != null)
            {
                health.HealthChanged -= OnHealthChanged;
            }

            mech = target;
            movement = mech.GetComponent<MechMovement>();
            health = mech.GetComponent<HealthSystem>();
            lockOn = mech.GetComponent<LockOnSystem>();
            ability = mech.GetComponent<MechSpecialAbility>();

            if (health != null)
            {
                health.HealthChanged += OnHealthChanged;
                OnHealthChanged(health.CurrentHealth, health.MaxHealth, health.CurrentShield, health.MaxShield);
            }

            RefreshModelLabel();
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

            if (ability != null)
            {
                if (abilityBar != null)
                {
                    abilityBar.value = ability.CooldownNormalized;
                }

                if (abilityLabel != null)
                {
                    abilityLabel.text = ability.IsReady
                        ? $"技能就绪 [{ability.AbilityId}]"
                        : $"技能冷却 {ability.CooldownNormalized * 100f:F0}%";
                }
            }
        }

        private void RefreshModelLabel()
        {
            if (modelLabel == null || mech == null)
            {
                return;
            }

            var def = MechModelCatalog.Get(mech.ModelId);
            modelLabel.text = $"{def.Code} {def.DisplayNameZh}";
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
