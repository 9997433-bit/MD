using System;
using System.Collections.Generic;
using System.Linq;

namespace Aetherboard.Core
{
    public class BattleEngine
    {
        private Random _rng;
        private IBossProfile _profile;
        private int _seed;

        public BattleState State { get; private set; }
        public string BossId { get; private set; }
        public int RandomSeed => _seed;

        public BattleEngine(string bossId = "earth", int seed = 7)
        {
            BossId = bossId;
            _seed = seed;
            _profile = BossRegistry.Get(bossId);
            _rng = new Random(seed);
            State = NewState();
        }

        private BattleState NewState()
        {
            return new BattleState
            {
                Turn = 1,
                Phase = BattlePhase.Warning,
                BoardSize = BoardMath.DefaultSize,
                Cells = BoardMath.MakeBoard(),
                Party = JobCatalog.CreateParty(),
                Boss = _profile.Create(),
            };
        }

        public void Reset(int? seed = null, string bossId = null)
        {
            if (seed.HasValue)
            {
                _seed = seed.Value;
                _rng = new Random(seed.Value);
            }
            if (!string.IsNullOrEmpty(bossId))
            {
                BossId = bossId;
                _profile = BossRegistry.Get(bossId);
            }
            State = NewState();
            BeginWarning();
        }

        public void RestoreState(BattleState snapshot, string bossId)
        {
            if (!string.IsNullOrEmpty(bossId))
            {
                BossId = bossId;
                _profile = BossRegistry.Get(bossId);
            }
            State = BattleStateCodec.Clone(snapshot);
            if (string.IsNullOrEmpty(State.Boss.BossId))
                State.Boss.BossId = BossId;
        }

        public void AddLog(string msg) => State.Log.Add(msg);

        public List<UnitState> LivingParty() => State.Party.Where(u => u.Alive).ToList();

        public float PartyDamageMultiplier() =>
            State.Party.Any(u => u.Alive && u.BardSongTurns > 0) ? 1.2f : 1f;

        public void BeginWarning()
        {
            if (State.Phase is BattlePhase.Victory or BattlePhase.Defeat) return;
            _profile.UpdatePhase(State.Boss);
            var telegraph = _profile.PickTelegraph(State.Boss, _rng);
            State.Boss.Telegraph = telegraph;
            if (telegraph is TelegraphKind.EarthenFury or TelegraphKind.Cyclone or TelegraphKind.Blizzard && State.Boss.FuryCastTurns == 0)
                State.Boss.FuryCastTurns = 2;

            State.PendingHazards = RollPendingHazards(telegraph);
            var preview = _profile.Preview(telegraph, State.BoardSize, State.Boss);
            State.PreviewCells = State.PendingHazards.Count > 0
                ? new List<GridPos>(State.PendingHazards)
                : new List<GridPos>(preview.DangerCells);

            if (!string.IsNullOrEmpty(preview.Message))
                AddLog($"[预警] {preview.Message}");
            if (telegraph == TelegraphKind.Earthquake && State.PendingHazards.Count > 0)
            {
                var c = State.PendingHazards[State.PendingHazards.Count / 2];
                AddLog($"[预警] 地震中心约在 ({c.X}, {c.Y})。");
            }
            if (telegraph == TelegraphKind.FrozenGround && State.PendingHazards.Count > 0)
            {
                var c = State.PendingHazards[0];
                AddLog($"[预警] 霜冻区域约在 ({c.X}, {c.Y}) 附近。");
            }
            State.Phase = BattlePhase.Move;
        }

        private List<GridPos> RollPendingHazards(TelegraphKind telegraph)
        {
            if (telegraph == TelegraphKind.Earthquake)
            {
                var center = new GridPos(_rng.Next(1, State.BoardSize - 1), _rng.Next(1, State.BoardSize - 1));
                return BoardMath.PositionsInRadius(center, 1, State.BoardSize);
            }
            if (telegraph == TelegraphKind.FrozenGround)
            {
                var topLeft = new GridPos(_rng.Next(1, State.BoardSize - 3), _rng.Next(1, State.BoardSize - 3));
                return BoardMath.Positions2x2(topLeft, State.BoardSize);
            }
            return new List<GridPos>(_profile.Preview(telegraph, State.BoardSize, State.Boss).DangerCells);
        }

        public bool CanMove(string unitId, GridPos dest)
        {
            var unit = State.Party.First(u => u.Id == unitId);
            if (!unit.Alive || unit.MovedThisTurn || State.Phase != BattlePhase.Move) return false;
            if (!dest.InBounds(State.BoardSize)) return false;
            if (BoardMath.IsDeadly(State.Cells, dest)) return false;
            if (dest.Equals(unit.Pos)) return false;
            if (dest.Equals(BoardMath.BossPos(State.BoardSize))) return false;
            if (State.Party.Any(u => u.Alive && u.Id != unitId && u.Pos.Equals(dest))) return false;
            return unit.Pos.Distance(dest) <= JobCatalog.MoveRange[unit.Job];
        }

        public bool MoveUnit(string unitId, GridPos dest)
        {
            if (!CanMove(unitId, dest)) return false;
            var unit = State.Party.First(u => u.Id == unitId);
            unit.Pos = dest;
            unit.MovedThisTurn = true;
            AddLog($"{unit.DisplayName} 移动到 ({dest.X}, {dest.Y})。");
            return true;
        }

        public bool CanUseSkill(string unitId, string skillId, GridPos? target = null)
        {
            var unit = State.Party.First(u => u.Id == unitId);
            if (!unit.Alive) return false;
            if (skillId == "interrupt")
                return State.Phase == BattlePhase.Weave && !unit.OgcdUsed && State.Boss.FuryCastTurns > 0;
            var skill = SkillCatalog.Get(skillId);
            if (skill.Kind == "gcd")
            {
                if (State.Phase != BattlePhase.Action || unit.GcdUsed) return false;
            }
            else if (State.Phase != BattlePhase.Weave || unit.OgcdUsed) return false;

            if (!JobCatalog.JobSkills[unit.Job].Contains(skillId)) return false;
            if (skill.Range == 0) return true;
            if (!target.HasValue) return false;
            if (skill.Heal > 0)
                return State.Party.Any(u => u.Alive && u.Pos.Equals(target.Value));
            return target.Value.InBounds(State.BoardSize);
        }

        public bool UseSkill(string unitId, string skillId, GridPos? target = null)
        {
            if (!CanUseSkill(unitId, skillId, target)) return false;
            var unit = State.Party.First(u => u.Id == unitId);
            var skill = SkillCatalog.Get(skillId);
            if (skill.Kind == "gcd") unit.GcdUsed = true;
            else unit.OgcdUsed = true;

            if (skill.Heal > 0 && target.HasValue)
                ApplyHeal(unit, skill, target.Value);
            else if (skillId == "interrupt")
            {
                State.Boss.FuryCastTurns = -1;
                AddLog($"{unit.DisplayName} 打断了{_profile.FuryName}！");
            }
            else if (skillId is "rampart" or "manaward")
            {
                unit.MitTurns = skill.MitDuration;
                AddLog($"{unit.DisplayName} 获得 {skill.MitDuration} 回合减伤。");
            }
            else if (skillId == "provoke")
            {
                unit.TauntTurns = 1;
                AddLog($"{unit.DisplayName} 挑衅 Boss。");
            }
            else if (skillId == "mages_ballad")
            {
                foreach (var ally in LivingParty()) ally.BardSongTurns = 3;
                AddLog($"{unit.DisplayName} 开启魔人歌。");
            }
            else if (skillId == "repelling_shot")
            {
                ApplyBossDamage((int)(skill.Power * PartyDamageMultiplier()));
                Repel(unit);
            }
            else
                ApplyPartyOffensive(unit, skill);

            return true;
        }

        private void ApplyPartyOffensive(UnitState unit, SkillDef skill)
        {
            var power = skill.Power;
            if (unit.Job == JobType.BlackMage && skill.Id == "fire" && !unit.MovedThisTurn)
            {
                power = (int)(power * 1.5f);
                AddLog($"{unit.DisplayName} 站桩读条，火炎强化。");
            }
            if (unit.Job == JobType.Bard && skill.Id == "straight_shot" && unit.BardSongTurns > 0)
                power = (int)(power * 1.3f);
            var damage = (int)(power * PartyDamageMultiplier());
            ApplyBossDamage(damage);
            AddLog($"{unit.DisplayName} 使用 {skill.Name}，造成 {damage} 点伤害。");
        }

        private void ApplyBossDamage(int damage)
        {
            State.Boss.Hp = Math.Max(0, State.Boss.Hp - damage);
            if (State.Boss.Hp == 0)
            {
                State.Boss.Alive = false;
                State.Phase = BattlePhase.Victory;
                AddLog(_profile.VictoryMessage);
            }
        }

        private void ApplyHeal(UnitState unit, SkillDef skill, GridPos target)
        {
            List<UnitState> targets;
            if (skill.AoeRadius > 0)
                targets = LivingParty().Where(u => u.Pos.Distance(target) <= skill.AoeRadius).ToList();
            else
                targets = LivingParty().Where(u => u.Pos.Equals(target)).ToList();
            foreach (var ally in targets)
            {
                ally.Hp = skill.Heal >= 9999 ? ally.MaxHp : Math.Min(ally.MaxHp, ally.Hp + skill.Heal);
                AddLog($"{unit.DisplayName} 治疗 {ally.DisplayName}。");
            }
        }

        private void Repel(UnitState unit)
        {
            var boss = BoardMath.BossPos(State.BoardSize);
            var dx = unit.Pos.X - boss.X;
            var dy = unit.Pos.Y - boss.Y;
            if (dx == 0 && dy == 0) dy = 1;
            var stepX = dx == 0 ? 0 : dx > 0 ? 1 : -1;
            var stepY = dy == 0 ? 1 : dy > 0 ? 1 : -1;
            var dest = new GridPos(unit.Pos.X + stepX, unit.Pos.Y + stepY);
            if (dest.InBounds(State.BoardSize) && !BoardMath.IsDeadly(State.Cells, dest))
            {
                if (!State.Party.Any(u => u.Alive && u.Id != unit.Id && u.Pos.Equals(dest)))
                    unit.Pos = dest;
            }
        }

        private void HitUnit(UnitState unit, int raw)
        {
            var damage = unit.MitTurns > 0 ? (int)(raw * 0.6f) : raw;
            unit.Hp = Math.Max(0, unit.Hp - damage);
            if (unit.Hp == 0)
            {
                unit.Alive = false;
                AddLog($"{unit.DisplayName} 倒下了。");
            }
        }

        public void AutoFillMissingActions()
        {
            if (State.Phase == BattlePhase.Weave && State.Boss.FuryCastTurns > 0)
            {
                var knight = LivingParty().FirstOrDefault(u => u.Job == JobType.Knight && !u.OgcdUsed);
                knight?.Let(k => UseSkill(k.Id, "interrupt", BoardMath.BossPos(State.BoardSize)));
            }

            foreach (var unit in LivingParty())
            {
                if (State.Phase == BattlePhase.Move && !unit.MovedThisTurn)
                {
                    var dest = TacticalAI.PickMoveDest(unit, State);
                    if (!dest.Equals(unit.Pos)) MoveUnit(unit.Id, dest);
                    else unit.MovedThisTurn = true;
                }
                else if (State.Phase == BattlePhase.Action && !unit.GcdUsed)
                {
                    UseSkill(unit.Id, TacticalAI.PickGcdSkill(unit, State), TacticalAI.PickGcdTarget(unit, State));
                }
                else if (State.Phase == BattlePhase.Weave && !unit.OgcdUsed)
                {
                    var choice = TacticalAI.PickOgcd(unit, State);
                    if (choice.HasValue)
                        UseSkill(unit.Id, choice.Value.skillId, choice.Value.target);
                }
            }
        }

        public void ResolveTurn()
        {
            if (State.Phase != BattlePhase.Resolve) return;
            var telegraph = State.Boss.Telegraph;
            BoardMath.ClearHazards(State.Cells, State.BoardSize);

            var (hazards, logs) = _profile.ResolveMechanic(telegraph, State.Boss, State.BoardSize, _rng);
            if (telegraph == TelegraphKind.Earthquake && State.PendingHazards.Count > 0)
                hazards = new List<GridPos>(State.PendingHazards);
            if (telegraph == TelegraphKind.FrozenGround && State.PendingHazards.Count > 0)
                hazards = new List<GridPos>(State.PendingHazards);
            foreach (var entry in logs) AddLog(entry);

            if (hazards.Count > 0 && telegraph is TelegraphKind.Shrink or TelegraphKind.Earthquake or TelegraphKind.FrozenGround)
            {
                BoardMath.ApplyHazards(State.Cells, hazards);
                var mechDmg = _profile.MechanicDamage(telegraph);
                if (mechDmg > 0)
                {
                    foreach (var unit in LivingParty())
                        if (hazards.Any(h => h.Equals(unit.Pos)))
                            HitUnit(unit, mechDmg);
                }
            }
            else if (hazards.Count > 0)
            {
                var mechDmg = _profile.MechanicDamage(telegraph);
                foreach (var unit in LivingParty())
                    if (hazards.Any(h => h.Equals(unit.Pos)))
                        HitUnit(unit, mechDmg);
            }

            if (telegraph is TelegraphKind.EarthenFury or TelegraphKind.Cyclone or TelegraphKind.Blizzard && State.Boss.FuryCastTurns == 0)
            {
                var dmg = _profile.MechanicDamage(telegraph);
                foreach (var unit in LivingParty()) HitUnit(unit, dmg);
            }

            if (_profile is WindSovereignProfile wind)
            {
                if (wind.IsSpread(telegraph)) ResolveSpread();
                if (wind.IsStack(telegraph)) ResolveStack();
            }

            if (_profile.IsIceRing(telegraph)) ResolveIceRing();

            var tank = LivingParty().FirstOrDefault(u => u.Job == JobType.Knight);
            var living = LivingParty();
            if (living.Count > 0)
            {
                var target = tank is { TauntTurns: > 0 } ? tank : living[_rng.Next(living.Count)];
                HitUnit(target, _profile.BasicDamage(State.Boss));
                AddLog($"Boss 攻击 {target.DisplayName}。");
            }

            foreach (var unit in LivingParty().ToList())
            {
                if (BoardMath.IsDeadly(State.Cells, unit.Pos))
                {
                    unit.Alive = false;
                    unit.Hp = 0;
                    AddLog($"{unit.DisplayName} 站在即死区，被淘汰。");
                }
            }

            foreach (var unit in LivingParty())
            {
                if (unit.MitTurns > 0) unit.MitTurns--;
                if (unit.TauntTurns > 0) unit.TauntTurns--;
                if (unit.BardSongTurns > 0) unit.BardSongTurns--;
                unit.ResetTurnFlags();
            }

            if (LivingParty().Count == 0)
            {
                State.Phase = BattlePhase.Defeat;
                AddLog("全队阵亡，战斗失败。");
                return;
            }
            if (!State.Boss.Alive)
            {
                State.Phase = BattlePhase.Victory;
                return;
            }

            State.Turn++;
            State.Boss.Telegraph = TelegraphKind.None;
            BeginWarning();
        }

        private void ResolveSpread()
        {
            var living = LivingParty();
            var hit = new HashSet<string>();
            for (var i = 0; i < living.Count; i++)
            for (var j = i + 1; j < living.Count; j++)
                if (living[i].Pos.Distance(living[j].Pos) <= 1)
                {
                    hit.Add(living[i].Id);
                    hit.Add(living[j].Id);
                }
            var dmg = _profile.MechanicDamage(TelegraphKind.Spread);
            foreach (var unit in living.Where(u => hit.Contains(u.Id)))
            {
                HitUnit(unit, dmg);
                AddLog($"{unit.DisplayName} 未能分散，受到 {dmg} 伤害。");
            }
        }

        private void ResolveStack()
        {
            var center = BoardMath.BoardCenter(State.BoardSize);
            var dmg = _profile.MechanicDamage(TelegraphKind.Stack);
            foreach (var unit in LivingParty())
            {
                if (unit.Pos.Distance(center) > 1)
                {
                    HitUnit(unit, dmg);
                    AddLog($"{unit.DisplayName} 未能集合，受到 {dmg} 伤害。");
                }
            }
        }

        private void ResolveIceRing()
        {
            var center = BoardMath.BoardCenter(State.BoardSize);
            var dmg = _profile.MechanicDamage(TelegraphKind.IceRing);
            foreach (var unit in LivingParty())
            {
                if (unit.Pos.Distance(center) != 2)
                {
                    HitUnit(unit, dmg);
                    AddLog($"{unit.DisplayName} 未站在冰环上，受到 {dmg} 伤害。");
                }
            }
        }

        public void AdvanceAfterMoves()
        {
            if (State.Phase == BattlePhase.Move) State.Phase = BattlePhase.Action;
        }

        public void AdvanceAfterActions()
        {
            if (State.Phase == BattlePhase.Action) State.Phase = BattlePhase.Weave;
        }

        public void AdvanceAfterWeaves()
        {
            if (State.Phase == BattlePhase.Weave)
            {
                State.Phase = BattlePhase.Resolve;
                ResolveTurn();
            }
        }

        public void EndPhase()
        {
            if (State.Phase is BattlePhase.Victory or BattlePhase.Defeat) return;
            AutoFillMissingActions();
            switch (State.Phase)
            {
                case BattlePhase.Move: AdvanceAfterMoves(); break;
                case BattlePhase.Action: AdvanceAfterActions(); break;
                case BattlePhase.Weave: AdvanceAfterWeaves(); break;
            }
        }

        public void StepAuto()
        {
            if (State.Phase is BattlePhase.Victory or BattlePhase.Defeat) return;
            if (State.Phase == BattlePhase.Warning) BeginWarning();
            while (State.Phase == BattlePhase.Move)
            {
                AutoFillMissingActions();
                if (State.Party.All(u => u.MovedThisTurn || !u.Alive)) AdvanceAfterMoves();
            }
            while (State.Phase == BattlePhase.Action)
            {
                AutoFillMissingActions();
                if (State.Party.All(u => u.GcdUsed || !u.Alive)) AdvanceAfterActions();
            }
            if (State.Phase == BattlePhase.Weave)
            {
                AutoFillMissingActions();
                AdvanceAfterWeaves();
            }
        }
    }

    internal static class FunctionalExtensions
    {
        public static void Let<T>(this T item, Action<T> action) => action(item);
    }
}
