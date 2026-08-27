using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Radial GCD / oGCD skill menu attached near the active piece or on the off-hand wrist.
    /// </summary>
    public class SkillRingController : MonoBehaviour
    {
        [SerializeField] private BattleDirector director;
        [SerializeField] private Transform ringAnchor;
        [SerializeField] private float radius = 0.08f;
        [SerializeField] private SkillRingButton buttonPrefab;

        private readonly List<SkillRingButton> _buttons = new();
        private string _activeUnitId;

        public void ShowForUnit(string unitId, JobType job)
        {
            _activeUnitId = unitId;
            ClearButtons();
            var skills = JobCatalog.JobSkills[job];
            for (var i = 0; i < skills.Length; i++)
            {
                var skillId = skills[i];
                var def = SkillCatalog.Get(skillId);
                var angle = i * (360f / skills.Length) * Mathf.Deg2Rad;
                var pos = new Vector3(Mathf.Cos(angle), 0.02f, Mathf.Sin(angle)) * radius;
                var btn = Instantiate(buttonPrefab, ringAnchor);
                btn.transform.localPosition = pos;
                btn.Setup(def.Name, def.Kind, () => OnSkillSelected(skillId));
                _buttons.Add(btn);
            }
            if (director.State.Boss.FuryCastTurns > 0)
            {
                var btn = Instantiate(buttonPrefab, ringAnchor);
                btn.transform.localPosition = Vector3.up * 0.06f;
                btn.Setup("打断", "ogcd", () => OnSkillSelected("interrupt"));
                _buttons.Add(btn);
            }
            ringAnchor.gameObject.SetActive(true);
        }

        public void Hide()
        {
            ringAnchor.gameObject.SetActive(false);
            ClearButtons();
        }

        private void OnSkillSelected(string skillId)
        {
            var target = BoardMath.BossPos(BoardMath.DefaultSize);
            director.TryUseSkill(_activeUnitId, skillId, target);
            Hide();
        }

        private void ClearButtons()
        {
            foreach (var b in _buttons)
                if (b != null) Destroy(b.gameObject);
            _buttons.Clear();
        }
    }

    public class SkillRingButton : MonoBehaviour
    {
        [SerializeField] private UnityEngine.UI.Text label;

        public void Setup(string text, string kind, System.Action onClick)
        {
            if (label != null) label.text = $"{text}\n({kind})";
            // Wire XR simple push button or Unity UI onClick in prefab.
        }
    }
}
