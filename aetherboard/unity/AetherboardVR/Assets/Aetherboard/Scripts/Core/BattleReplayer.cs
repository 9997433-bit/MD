namespace Aetherboard.Core
{
    /// <summary>
    /// Replays a recorded command log on a fresh seeded engine.
    /// </summary>
    public static class BattleReplayer
    {
        public static BattleState Replay(BattleCommandLog log)
        {
            var engine = new BattleEngine(log.BossId, log.RandomSeed);
            engine.BeginWarning();
            foreach (var cmd in log.Commands)
                BattleCommandExecutor.Apply(engine, cmd);
            return BattleStateCodec.Clone(engine.State);
        }

        public static BattleEngine ReplayToEngine(BattleCommandLog log)
        {
            var engine = new BattleEngine(log.BossId, log.RandomSeed);
            engine.BeginWarning();
            foreach (var cmd in log.Commands)
                BattleCommandExecutor.Apply(engine, cmd);
            return engine;
        }
    }
}
