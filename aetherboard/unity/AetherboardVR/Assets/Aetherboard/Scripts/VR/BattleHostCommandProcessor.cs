using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Shared host-side command validation and application for TCP / WS / NGO ingress.
    /// </summary>
    public static class BattleHostCommandProcessor
    {
        public sealed class Result
        {
            public bool Ok;
            public string ErrorMessage;
            public bool StateChanged;
        }

        public static Result TryApply(BattleDirector director, CoopController coop, bool enforceCoop, string line)
        {
            if (director == null)
                return Fail("No battle director");

            var cmd = BattleSyncProtocol.ExtractCommand(line);
            if (cmd == null)
                return Fail("Invalid command");

            var coopOn = enforceCoop && coop != null && coop.Mode == CoopMode.SplitCoop;
            if (coopOn && CoopRules.CommandRequiresUnit(cmd.Type) &&
                !CoopRules.CanControl(cmd.PlayerId, cmd.UnitId, true))
                return Fail($"P{cmd.PlayerId} 无权控制 {cmd.UnitId}");

            var ok = BattleCommandExecutor.Apply(director.Engine, cmd);
            if (!ok)
                return Fail("Command rejected");

            return new Result { Ok = true, StateChanged = true };
        }

        private static Result Fail(string message) =>
            new() { Ok = false, ErrorMessage = message };
    }
}
