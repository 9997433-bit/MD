namespace Aetherboard.Core
{
    public static class BattleCommandExecutor
    {
        public static bool Apply(BattleEngine engine, BattleCommand cmd)
        {
            switch (cmd.Type)
            {
                case BattleCommandType.Move:
                    return engine.MoveUnit(cmd.UnitId, new GridPos(cmd.TargetX, cmd.TargetY));
                case BattleCommandType.Skill:
                {
                    GridPos? target = cmd.TargetX >= 0 && cmd.TargetY >= 0
                        ? new GridPos(cmd.TargetX, cmd.TargetY)
                        : null;
                    return engine.UseSkill(cmd.UnitId, cmd.SkillId, target);
                }
                case BattleCommandType.EndPhase:
                    engine.EndPhase();
                    return true;
                case BattleCommandType.SetBoss:
                    engine.Reset(null, cmd.BossId);
                    return true;
                default:
                    return false;
            }
        }
    }
}
