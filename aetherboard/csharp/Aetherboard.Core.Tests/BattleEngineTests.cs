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

        [Fact]
        public void Snapshot_RoundTrip_PreservesState()
        {
            var engine = new BattleEngine("wind", 99);
            engine.BeginWarning();
            Assert.True(engine.MoveUnit("knight", new GridPos(3, 6)));
            engine.State.Boss.Hp = 4200;

            var json = BattleStateCodec.Serialize(engine.State, engine.BossId);
            var (restored, bossId) = BattleStateCodec.Deserialize(json);

            Assert.Equal("wind", bossId);
            Assert.Equal(engine.State.Turn, restored.Turn);
            Assert.Equal(engine.State.Phase, restored.Phase);
            Assert.Equal(4200, restored.Boss.Hp);
            Assert.Equal(new GridPos(3, 6), restored.Party.Find(u => u.Id == "knight")!.Pos);
        }

        [Fact]
        public void RestoreState_MatchesSnapshot()
        {
            var engine = new BattleEngine("earth", 7);
            engine.BeginWarning();
            Assert.True(engine.MoveUnit("bard", new GridPos(3, 3)));
            var snapshot = BattleStateCodec.Clone(engine.State);

            engine.StepAuto();
            Assert.NotEqual(engine.State.Turn, snapshot.Turn);

            engine.RestoreState(snapshot, "earth");
            Assert.Equal(snapshot.Turn, engine.State.Turn);
            Assert.Equal(new GridPos(3, 3), engine.State.Party.Find(u => u.Id == "bard")!.Pos);
        }

        [Fact]
        public void HostAuthority_AppliesMove()
        {
            var host = new BattleHostAuthority("earth", 42);
            var cmd = new BattleCommand
            {
                Type = BattleCommandType.Move,
                UnitId = "knight",
                TargetX = 3,
                TargetY = 6
            };
            var (ok, _, err) = host.ApplyCommand(cmd);
            Assert.True(ok);
            Assert.Null(err);
            Assert.Equal(new GridPos(3, 6), host.Engine.State.Party.Find(u => u.Id == "knight")!.Pos);
        }

        [Fact]
        public void Replayer_MatchesLiveCommands()
        {
            var live = new BattleEngine("earth", 42);
            live.BeginWarning();
            var log = new BattleCommandLog { RandomSeed = 42, BossId = "earth" };
            var move = new BattleCommand
            {
                Type = BattleCommandType.Move,
                UnitId = "knight",
                TargetX = 3,
                TargetY = 6
            };
            BattleCommandExecutor.Apply(live, move);
            log.Record(move);
            log.Record(new BattleCommand { Type = BattleCommandType.EndPhase });

            var replayed = BattleReplayer.Replay(log);
            Assert.Equal(live.State.Turn, replayed.Turn);
            Assert.Equal(
                live.State.Party.Find(u => u.Id == "knight")!.Pos,
                replayed.Party.Find(u => u.Id == "knight")!.Pos);
        }

        [Fact]
        public void SyncProtocol_RoundTripCommand()
        {
            var cmd = new BattleCommand
            {
                Type = BattleCommandType.Skill,
                UnitId = "knight",
                SkillId = "shield_bash",
                TargetX = 3,
                TargetY = 3
            };
            var line = BattleSyncProtocol.EncodeCommand(cmd);
            var parsed = BattleSyncProtocol.ExtractCommand(line);
            Assert.NotNull(parsed);
            Assert.Equal(BattleCommandType.Skill, parsed!.Type);
            Assert.Equal("shield_bash", parsed.SkillId);
        }
    }
}
