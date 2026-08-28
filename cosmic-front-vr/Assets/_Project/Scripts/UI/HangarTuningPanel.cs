using System;
using System.Text;
using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Tuning;

namespace CosmicFront.UI
{
    /// <summary>
    /// Code-driven hangar tuning UI: 3 passive slots, equip/unequip.
    /// Optional Text/button refs; works fully via public API without scene wiring.
    /// </summary>
    public class HangarTuningPanel : MonoBehaviour
    {
        [SerializeField] private UnityEngine.UI.Text statusText;
        [SerializeField] private UnityEngine.UI.Text[] slotLabels = new UnityEngine.UI.Text[PilotLoadout.MaxSlots];
        [SerializeField] private UnityEngine.UI.Text catalogText;

        private PilotLoadout _loadout = new PilotLoadout();

        public PilotLoadout Loadout => _loadout;
        public event Action LoadoutChanged;

        private void Awake()
        {
            SyncFromGameManager();
            RefreshUi();
        }

        private void OnEnable()
        {
            SyncFromGameManager();
            RefreshUi();
        }

        public void BindLoadout(PilotLoadout loadout)
        {
            _loadout = loadout ?? new PilotLoadout();
            PushToGameManager();
            RefreshUi();
            LoadoutChanged?.Invoke();
        }

        public void SyncFromGameManager()
        {
            if (GameManager.Instance != null && GameManager.Instance.PilotLoadout != null)
            {
                _loadout = GameManager.Instance.PilotLoadout;
            }
            else if (_loadout == null)
            {
                _loadout = new PilotLoadout();
            }
        }

        public void PushToGameManager()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SetPilotLoadout(_loadout);
            }
        }

        /// <summary>Equip catalog mod into slot if points allow.</summary>
        public bool Equip(int slot, PassiveMod mod)
        {
            EnsureLoadout();
            if (!_loadout.TryEquip(slot, mod))
            {
                RefreshUi();
                return false;
            }

            PushToGameManager();
            RefreshUi();
            LoadoutChanged?.Invoke();
            return true;
        }

        public bool EquipById(int slot, string modId)
        {
            return Equip(slot, PassiveMod.FindById(modId));
        }

        public bool Unequip(int slot)
        {
            EnsureLoadout();
            if (!_loadout.Unequip(slot))
            {
                return false;
            }

            PushToGameManager();
            RefreshUi();
            LoadoutChanged?.Invoke();
            return true;
        }

        public void ClearAll()
        {
            EnsureLoadout();
            _loadout.Clear();
            PushToGameManager();
            RefreshUi();
            LoadoutChanged?.Invoke();
        }

        public string DescribeSlots()
        {
            EnsureLoadout();
            var sb = new StringBuilder();
            sb.AppendLine($"调校点数: {_loadout.AvailablePoints}/{_loadout.PointBudget}");
            for (var i = 0; i < PilotLoadout.MaxSlots; i++)
            {
                var mod = _loadout.GetSlot(i);
                sb.AppendLine(mod == null
                    ? $"槽 {i + 1}: （空）"
                    : $"槽 {i + 1}: {mod.DisplayName} — {mod.Description} (耗{mod.Cost})");
            }

            return sb.ToString().TrimEnd();
        }

        public string DescribeCatalog()
        {
            var sb = new StringBuilder();
            sb.AppendLine("可用被动:");
            foreach (var mod in PassiveMod.Catalog)
            {
                sb.AppendLine($"[{mod.Id}] {mod.DisplayName} ({mod.Description}) 耗点{mod.Cost}");
            }

            return sb.ToString().TrimEnd();
        }

        public void RefreshUi()
        {
            EnsureLoadout();

            if (statusText != null)
            {
                statusText.text = DescribeSlots();
            }

            if (slotLabels != null)
            {
                for (var i = 0; i < slotLabels.Length && i < PilotLoadout.MaxSlots; i++)
                {
                    if (slotLabels[i] == null)
                    {
                        continue;
                    }

                    var mod = _loadout.GetSlot(i);
                    slotLabels[i].text = mod == null
                        ? $"槽 {i + 1}: 空"
                        : $"槽 {i + 1}: {mod.DisplayName}";
                }
            }

            if (catalogText != null)
            {
                catalogText.text = DescribeCatalog();
            }
        }

        // Optional UnityEvent/button hooks
        public void UiEquipMoveSpeedSlot0() => Equip(0, PassiveMod.MoveSpeedPlus5);
        public void UiEquipShieldSlot1() => Equip(1, PassiveMod.ShieldPlus10);
        public void UiEquipCooldownSlot2() => Equip(2, PassiveMod.CooldownMinus5);
        public void UiUnequipSlot0() => Unequip(0);
        public void UiUnequipSlot1() => Unequip(1);
        public void UiUnequipSlot2() => Unequip(2);

        private void EnsureLoadout()
        {
            if (_loadout == null)
            {
                _loadout = new PilotLoadout();
            }
        }
    }
}
