using System;
using UnityEngine;

namespace CosmicFront.Tuning
{
    /// <summary>
    /// Hangar pilot loadout: up to 3 equipped passive mods and remaining point budget.
    /// </summary>
    [Serializable]
    public class PilotLoadout
    {
        public const int MaxSlots = 3;
        public const int DefaultPointBudget = 3;

        [SerializeField] private PassiveMod[] equipped = new PassiveMod[MaxSlots];
        [SerializeField] private int pointBudget = DefaultPointBudget;

        public int PointBudget
        {
            get => pointBudget;
            set => pointBudget = Mathf.Max(0, value);
        }

        public int SpentPoints
        {
            get
            {
                var spent = 0;
                for (var i = 0; i < MaxSlots; i++)
                {
                    if (equipped[i] != null)
                    {
                        spent += Mathf.Max(0, equipped[i].Cost);
                    }
                }

                return spent;
            }
        }

        public int AvailablePoints => Mathf.Max(0, pointBudget - SpentPoints);

        public PilotLoadout()
        {
            EnsureSlots();
        }

        public PilotLoadout(int budget)
        {
            pointBudget = Mathf.Max(0, budget);
            EnsureSlots();
        }

        public PassiveMod GetSlot(int index)
        {
            EnsureSlots();
            if (index < 0 || index >= MaxSlots)
            {
                return null;
            }

            return equipped[index];
        }

        public PassiveMod[] GetEquippedSnapshot()
        {
            EnsureSlots();
            var copy = new PassiveMod[MaxSlots];
            Array.Copy(equipped, copy, MaxSlots);
            return copy;
        }

        public bool HasAnyMod()
        {
            EnsureSlots();
            for (var i = 0; i < MaxSlots; i++)
            {
                if (equipped[i] != null)
                {
                    return true;
                }
            }

            return false;
        }

        public bool TryEquip(int slot, PassiveMod mod)
        {
            EnsureSlots();
            if (mod == null || slot < 0 || slot >= MaxSlots)
            {
                return false;
            }

            var current = equipped[slot];
            var freed = current != null ? Mathf.Max(0, current.Cost) : 0;
            var needed = Mathf.Max(0, mod.Cost);
            if (AvailablePoints + freed < needed)
            {
                return false;
            }

            equipped[slot] = mod;
            return true;
        }

        public bool Unequip(int slot)
        {
            EnsureSlots();
            if (slot < 0 || slot >= MaxSlots || equipped[slot] == null)
            {
                return false;
            }

            equipped[slot] = null;
            return true;
        }

        public void Clear()
        {
            EnsureSlots();
            for (var i = 0; i < MaxSlots; i++)
            {
                equipped[i] = null;
            }
        }

        private void EnsureSlots()
        {
            if (equipped == null || equipped.Length != MaxSlots)
            {
                var resized = new PassiveMod[MaxSlots];
                if (equipped != null)
                {
                    Array.Copy(equipped, resized, Math.Min(equipped.Length, MaxSlots));
                }

                equipped = resized;
            }
        }
    }
}
