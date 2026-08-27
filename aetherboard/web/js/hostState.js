/** Apply authoritative host state JSON to the local BattleEngine (display-only sync). */
import { BOSS_PROFILES } from "./bosses.js";
import { Phase } from "./constants.js";

export function importHostState(engine, payload) {
  engine.bossId = payload.bossId || engine.bossId;
  engine.profile = BOSS_PROFILES[engine.bossId] || BOSS_PROFILES.earth;
  engine.turn = payload.turn;
  engine.phase = payload.phase;
  engine.cells = payload.cells;
  engine.pendingHazards = (payload.pendingHazards || []).map((p) => ({ x: p.x, y: p.y }));
  engine.previewCells = (payload.previewCells || []).map((p) => ({ x: p.x, y: p.y }));

  const boss = payload.boss;
  engine.boss = {
    name: boss.name,
    hp: boss.hp,
    maxHp: boss.maxHp,
    phase: boss.phase,
    telegraph: boss.telegraph,
    fury: boss.furyCastTurns ?? 0,
    shrink: boss.shrinkLevel ?? 0,
    alive: boss.alive,
  };

  engine.party = payload.party.map((u) => ({
    id: u.id,
    name: u.name,
    job: u.job,
    pos: { x: u.pos.x, y: u.pos.y },
    hp: u.hp,
    maxHp: u.maxHp,
    alive: u.alive,
    moved: u.moved ?? u.movedThisTurn ?? false,
    gcd: u.gcdUsed ?? false,
    ogcd: u.ogcdUsed ?? false,
    mit: u.mitTurns ?? 0,
    song: u.songTurns ?? 0,
    taunt: u.tauntTurns ?? 0,
  }));

  engine.log = [...(payload.log || [])];
  engine.isRemote = true;
}
