using UnityEngine;
using UnityEngine.UI;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class BossHologramView : MonoBehaviour
    {
        [SerializeField] private Text nameLabel;
        [SerializeField] private Image hpFill;
        [SerializeField] private Text phaseLabel;
        [SerializeField] private Animator animator;

        public void Bind(BossState boss)
        {
            if (nameLabel != null) nameLabel.text = boss.Name;
            if (hpFill != null) hpFill.fillAmount = boss.MaxHp > 0 ? (float)boss.Hp / boss.MaxHp : 0f;
            if (phaseLabel != null) phaseLabel.text = $"P{boss.Phase}";
            if (animator != null && boss.FuryCastTurns > 0)
                animator.SetBool("Casting", true);
            else if (animator != null)
                animator.SetBool("Casting", false);
        }
    }
}
