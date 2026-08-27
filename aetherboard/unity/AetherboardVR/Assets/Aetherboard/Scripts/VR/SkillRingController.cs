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
        private SkillChip _hoveredChip;
        private string _activeUnitId;
        private string _pendingSkillId;
        private bool _awaitingTarget;

        public bool IsVisible => _ringAnchor != null && _ringAnchor.gameObject.activeSelf;
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
            ClearHover();
            ClearChips();

            var skills = new List<string>(JobCatalog.JobSkills[job]);
            if (_director.State.Boss.FuryCastTurns > 0) skills.Add("interrupt");

            CreateBackingDisc();

            for (var i = 0; i < skills.Count; i++)
            {
                var skillId = skills[i];
                var def = SkillCatalog.Skills.TryGetValue(skillId, out var s) ? s : null;
                if (def == null) continue;

                var angle = (i / (float)skills.Count) * Mathf.PI * 2f;
                var local = new Vector3(Mathf.Cos(angle), 0.04f, Mathf.Sin(angle)) * radius;
                var target = def.Heal > 0
                    ? _director.State.Party.Find(u => u.Id == unitId)?.Pos
                    : BoardMath.BossPos(BoardMath.DefaultSize);
                var enabled = _director.Engine.CanUseSkill(unitId, skillId, target);
                var chip = CreateChip(def.Name, def.Kind, local, skillId, enabled);
                _chips.Add(chip);
            }

            _ringAnchor.position = worldPos + Vector3.up * 0.12f;
            _ringAnchor.gameObject.SetActive(true);
            FaceCamera();
        }

        public void Hide()
        {
            ClearHover();
            _ringAnchor.gameObject.SetActive(false);
            _pendingSkillId = null;
            _awaitingTarget = false;
            ClearChips();
        }

        public void UpdateVrHover(Ray ray)
        {
            if (!IsVisible) return;
            if (VRRaycastUtility.TryHitSkillChip(ray, out var chip, out _) && _chips.Contains(chip))
                SetHoveredChip(chip);
            else
                SetHoveredChip(null);
        }

        public bool TryActivateFromRay(Ray ray)
        {
            if (!IsVisible) return false;
            if (VRRaycastUtility.TryHitSkillChip(ray, out var chip, out _))
                return ActivateSkill(chip.SkillId);
            if (_hoveredChip != null)
                return ActivateSkill(_hoveredChip.SkillId);
            return false;
        }

        public bool TrySelectChip(RaycastHit hit)
        {
            var chip = hit.collider.GetComponentInParent<SkillChip>();
            if (chip == null) return false;
            return ActivateSkill(chip.SkillId);
        }

        public bool ActivateSkill(string skillId)
        {
            var chip = _chips.Find(c => c.SkillId == skillId);
            if (chip != null && !chip.IsEnabled) return false;

            var def = SkillCatalog.Skills[skillId];
            var unit = _director.State.Party.Find(u => u.Id == _activeUnitId);
            if (unit == null) return false;

            if (def.Heal > 0)
            {
                _pendingSkillId = skillId;
                _awaitingTarget = true;
                VRHapticsUtility.PulseLight();
                return true;
            }

            var target = BoardMath.BossPos(BoardMath.DefaultSize);
            if (_director.TryUseSkill(_activeUnitId, skillId, target))
            {
                VRHapticsUtility.PulseMedium();
                Hide();
                return true;
            }
            VRHapticsUtility.PulseReject();
            return false;
        }

        public bool TryTargetCell(GridPos dest)
        {
            if (!_awaitingTarget || string.IsNullOrEmpty(_pendingSkillId)) return false;
            if (_director.TryUseSkill(_activeUnitId, _pendingSkillId, dest))
            {
                VRHapticsUtility.PulseMedium();
                Hide();
                return true;
            }
            VRHapticsUtility.PulseReject();
            return false;
        }

        private void CreateBackingDisc()
        {
            var disc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            disc.name = "SkillRingBacking";
            disc.transform.SetParent(_ringAnchor, false);
            disc.transform.localPosition = Vector3.zero;
            disc.transform.localScale = new Vector3(radius * 2.4f, 0.003f, radius * 2.4f);
            disc.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(0.05f, 0.08f, 0.12f, 0.82f));
            var col = disc.GetComponent<Collider>();
            if (col != null) Destroy(col);
        }

        private SkillChip CreateChip(string label, string kind, Vector3 localPos, string skillId, bool enabled)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = $"Skill_{skillId}";
            go.transform.SetParent(_ringAnchor, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = new Vector3(chipSize, 0.012f, chipSize);
            var r = go.GetComponent<Renderer>();

            var textGo = new GameObject("Label");
            textGo.transform.SetParent(go.transform, false);
            textGo.transform.localPosition = new Vector3(0, 1.5f, 0);
            textGo.transform.localScale = Vector3.one * 0.25f;
            var text = textGo.AddComponent<TextMesh>();
            text.text = label;
            text.fontSize = 32;
            text.characterSize = 0.05f;
            text.anchor = TextAnchor.MiddleCenter;
            text.color = enabled ? Color.white : new Color(1f, 1f, 1f, 0.45f);

            var chip = go.AddComponent<SkillChip>();
            chip.SkillId = skillId;
            chip.Init(r, kind, enabled);
            return chip;
        }

        private void SetHoveredChip(SkillChip chip)
        {
            if (_hoveredChip == chip) return;
            _hoveredChip?.SetHovered(false);
            _hoveredChip = chip;
            _hoveredChip?.SetHovered(true);
        }

        private void ClearHover() => SetHoveredChip(null);

        private void ClearChips()
        {
            foreach (var c in _chips)
                if (c != null) Destroy(c.gameObject);
            _chips.Clear();
            if (_ringAnchor != null)
            {
                for (var i = _ringAnchor.childCount - 1; i >= 0; i--)
                    Destroy(_ringAnchor.GetChild(i).gameObject);
            }
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
}
