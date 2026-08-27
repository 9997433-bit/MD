using System;
using System.Collections.Generic;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// World-space radial skill menu — procedural chips, clickable via mouse or VR ray.
    /// </summary>
    public class SkillRingController : MonoBehaviour
    {
        [SerializeField] private float radius = 0.09f;
        [SerializeField] private float chipSize = 0.035f;

        private BattleDirector _director;
        private BattleTableView _table;
        private Transform _ringAnchor;
        private readonly List<SkillChip> _chips = new();
        private string _activeUnitId;
        private string _pendingSkillId;
        private bool _awaitingTarget;

        public bool AwaitingTarget => _awaitingTarget;
        public string PendingSkillId => _pendingSkillId;

        public void Initialize(BattleDirector director, BattleTableView table, Transform parent)
        {
            _director = director;
            _table = table;
            _ringAnchor = new GameObject("SkillRing").transform;
            _ringAnchor.SetParent(parent, false);
            _ringAnchor.gameObject.SetActive(false);
        }

        public void ShowForUnit(string unitId, JobType job, Vector3 worldPos)
        {
            _activeUnitId = unitId;
            _pendingSkillId = null;
            _awaitingTarget = false;
            ClearChips();

            var skills = new List<string>(JobCatalog.JobSkills[job]);
            if (_director.State.Boss.FuryCastTurns > 0) skills.Add("interrupt");

            for (var i = 0; i < skills.Count; i++)
            {
                var skillId = skills[i];
                var def = SkillCatalog.Skills.TryGetValue(skillId, out var s) ? s : null;
                if (def == null) continue;

                var angle = (i / (float)skills.Count) * Mathf.PI * 2f;
                var local = new Vector3(Mathf.Cos(angle), 0.04f, Mathf.Sin(angle)) * radius;
                var chip = CreateChip(def.Name, def.Kind, local, skillId);
                _chips.Add(chip);
            }

            _ringAnchor.position = worldPos + Vector3.up * 0.12f;
            _ringAnchor.gameObject.SetActive(true);
            FaceCamera();
        }

        public void Hide()
        {
            _ringAnchor.gameObject.SetActive(false);
            _pendingSkillId = null;
            _awaitingTarget = false;
            ClearChips();
        }

        public bool TrySelectChip(RaycastHit hit)
        {
            var chip = hit.collider.GetComponent<SkillChip>();
            if (chip == null) return false;
            return ActivateSkill(chip.SkillId);
        }

        public bool ActivateSkill(string skillId)
        {
            var def = SkillCatalog.Skills[skillId];
            var unit = _director.State.Party.Find(u => u.Id == _activeUnitId);
            if (unit == null) return false;

            if (def.Heal > 0)
            {
                _pendingSkillId = skillId;
                _awaitingTarget = true;
                return true;
            }

            var target = BoardMath.BossPos(BoardMath.DefaultSize);
            if (_director.TryUseSkill(_activeUnitId, skillId, target))
            {
                Hide();
                return true;
            }
            return false;
        }

        public bool TryTargetCell(GridPos dest)
        {
            if (!_awaitingTarget || string.IsNullOrEmpty(_pendingSkillId)) return false;
            if (_director.TryUseSkill(_activeUnitId, _pendingSkillId, dest))
            {
                Hide();
                return true;
            }
            return false;
        }

        private SkillChip CreateChip(string label, string kind, Vector3 localPos, string skillId)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = $"Skill_{skillId}";
            go.transform.SetParent(_ringAnchor, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = new Vector3(chipSize, 0.008f, chipSize);
            var r = go.GetComponent<Renderer>();
            r.material = ProceduralAssets.CreateUnlitMaterial(
                kind == "ogcd" ? new Color(0.9f, 0.55f, 0.1f) : new Color(0.2f, 0.55f, 0.95f));

            var textGo = new GameObject("Label");
            textGo.transform.SetParent(go.transform, false);
            textGo.transform.localPosition = new Vector3(0, 1.5f, 0);
            textGo.transform.localScale = Vector3.one * 0.25f;
            var text = textGo.AddComponent<TextMesh>();
            text.text = label;
            text.fontSize = 32;
            text.characterSize = 0.05f;
            text.anchor = TextAnchor.MiddleCenter;
            text.color = Color.white;

            var chip = go.AddComponent<SkillChip>();
            chip.SkillId = skillId;
            return chip;
        }

        private void ClearChips()
        {
            foreach (var c in _chips)
                if (c != null) Destroy(c.gameObject);
            _chips.Clear();
        }

        private void LateUpdate()
        {
            if (_ringAnchor != null && _ringAnchor.gameObject.activeSelf)
                FaceCamera();
        }

        private void FaceCamera()
        {
            var cam = Camera.main;
            if (cam == null) return;
            _ringAnchor.rotation = Quaternion.LookRotation(
                _ringAnchor.position - cam.transform.position, Vector3.up);
        }
    }

    public class SkillChip : MonoBehaviour
    {
        public string SkillId;
    }
}
