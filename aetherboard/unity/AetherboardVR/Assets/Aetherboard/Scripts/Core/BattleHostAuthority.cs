namespace Aetherboard.Core
{
    /// <summary>
    /// Authoritative host: applies client commands and exports canonical state JSON.
    /// </summary>
    public class BattleHostAuthority
    {
        public BattleEngine Engine { get; }

        public BattleHostAuthority(string bossId = "earth", int seed = 42)
        {
            Engine = new BattleEngine(bossId, seed);
            Engine.BeginWarning();
        }

        public string ExportStateJson() =>
            BattleStateCodec.Serialize(Engine.State, Engine.BossId);

        public (bool ok, string stateJson, string error) ApplyCommand(BattleCommand cmd)
        {
            var ok = BattleCommandExecutor.Apply(Engine, cmd);
            if (!ok)
                return (false, ExportStateJson(), "Command rejected by battle rules.");
            return (true, ExportStateJson(), null);
        }

        public void ImportState(BattleState snapshot, string bossId) =>
            Engine.RestoreState(snapshot, bossId);
    }
}
