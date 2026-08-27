using System.Linq;
using Aetherboard.Core;
using Xunit;

namespace Aetherboard.Core.Tests
{
    public class BattleEngineTests
    {
        [Fact]
        public void Earth_AutoPlay_CanWin()
        {
            var wins = 0;
            for (var seed = 0; seed < 20; seed++)
            {
                var engine = new BattleEngine("earth", seed);
                engine.BeginWarning();
                for (var i = 0; i < 100; i++)
                {
                    if (engine.State.Phase is BattlePhase.Victory or BattlePhase.Defeat) break;
                    engine.StepAuto();
                }
                if (engine.State.Phase == BattlePhase.Victory) wins++;
            }
            Assert.True(wins > 0);
        }

        [Fact]
        public void Wind_AutoPlay_CanWin()
        {
            var wins = 0;
            for (var seed = 0; seed < 20; seed++)
            {
                var engine = new BattleEngine("wind", seed);
                engine.BeginWarning();
                for (var i = 0; i < 100; i++)
                {
                    if (engine.State.Phase is BattlePhase.Victory or BattlePhase.Defeat) break;
                    engine.StepAuto();
                }
                if (engine.State.Phase == BattlePhase.Victory) wins++;
            }
            Assert.True(wins > 0);
        }

        [Fact]
        public void Interrupt_PreventsFuryWipe()
        {
            var engine = new BattleEngine("earth", 0);
            engine.State.Boss.Phase = 3;
            engine.State.Boss.FuryCastTurns = 2;
            engine.State.Phase = BattlePhase.Weave;
            Assert.True(engine.UseSkill("knight", "interrupt", BoardMath.BossPos(7)));
            Assert.Equal(-1, engine.State.Boss.FuryCastTurns);
        }
    }
}
