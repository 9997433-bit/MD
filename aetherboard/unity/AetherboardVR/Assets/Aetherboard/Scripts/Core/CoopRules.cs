namespace Aetherboard.Core
{
    /// <summary>
    /// Split-coop ownership: P1 = 铁卫/游弦, P2 = 白愈/黑炎.
    /// </summary>
    public static class CoopRules
    {
        public static readonly string[] Player1Units = { "knight", "bard" };
        public static readonly string[] Player2Units = { "white_mage", "black_mage" };

        public static bool CanControl(int playerId, string unitId, bool coopEnabled)
        {
            if (!coopEnabled || playerId <= 0 || string.IsNullOrEmpty(unitId)) return true;
            var allowed = playerId == 1 ? Player1Units : Player2Units;
            foreach (var id in allowed)
                if (id == unitId) return true;
            return false;
        }

        public static bool CommandRequiresUnit(BattleCommandType type) =>
            type is BattleCommandType.Move or BattleCommandType.Skill;

        public static int OwnerOf(string unitId)
        {
            foreach (var id in Player1Units)
                if (id == unitId) return 1;
            foreach (var id in Player2Units)
                if (id == unitId) return 2;
            return 0;
        }
    }
}
