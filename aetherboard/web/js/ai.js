import { BOARD_SIZE, BOSS_POS, JOB_SKILLS, MOVE_RANGE, Telegraph } from "./constants.js";

function dist(a, b) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function posEq(a, b) {
  return a.x === b.x && a.y === b.y;
}

function edgePenalty(pos) {
  let s = 0;
  if (pos.x <= 0 || pos.x >= 6 || pos.y <= 0 || pos.y >= 6) s -= 40;
  else if (pos.x <= 1 || pos.x >= 5 || pos.y <= 1 || pos.y >= 5) s -= 15;
  return s;
}

function minDist(unit, pos, party) {
  const others = party.filter((u) => u.alive && u.id !== unit.id);
  if (!others.length) return 99;
  return Math.min(...others.map((u) => dist(u.pos, pos)));
}

export function scorePosition(unit, pos, engine) {
  const telegraph = engine.boss.telegraph;
  const center = { x: 3, y: 3 };
  let score = edgePenalty(pos);
  const party = engine.party.filter((u) => u.alive);

  if (telegraph === Telegraph.SLAM) score += dist(pos, center) * 3;
  else if (telegraph === Telegraph.EARTHQUAKE) {
    if (engine.pendingHazards?.some((p) => posEq(p, pos))) score -= 80;
    score += dist(pos, center) * 2;
  } else if (telegraph === Telegraph.SHRINK) {
    score += dist(pos, center) * 4;
    if (pos.y >= 5) score -= 25;
  } else if (telegraph === Telegraph.SPREAD) score += minDist(unit, pos, party) * 5;
  else if (telegraph === Telegraph.STACK) score -= dist(pos, center) * 4;
  else if (telegraph === Telegraph.GALE && pos.x === BOSS_POS.x) score -= 10;
  else if (telegraph === Telegraph.ICE_LANCE) {
    if (pos.x === BOSS_POS.x || pos.y === BOSS_POS.y) score -= 60;
  } else if (telegraph === Telegraph.FROZEN_GROUND) {
    if (engine.pendingHazards?.some((p) => posEq(p, pos))) score -= 80;
  }   else if (telegraph === Telegraph.ICE_RING) {
    if (dist(pos, center) === 2) score += 40;
    else score -= 30;
  } else if (telegraph === Telegraph.FLAME_BREATH) {
    if (Math.abs(pos.x - center.x) === Math.abs(pos.y - center.y)) score -= 60;
  } else if (telegraph === Telegraph.METEOR) {
    if (engine.pendingHazards?.some((p) => posEq(p, pos))) score -= 80;
  } else if (telegraph === Telegraph.HEAT_LINK) {
    score -= minDist(unit, pos, party) * 5;
  } else score += minDist(unit, pos, party);

  if (unit.job === "black_mage" && !posEq(pos, unit.pos)) score -= 2;
  if (unit.job === "knight" && telegraph !== Telegraph.SPREAD && telegraph !== Telegraph.HEAT_LINK) score -= dist(pos, BOSS_POS) * 2;
  return score;
}

export function reachable(unit, engine) {
  const occupied = new Set(
    engine.party.filter((u) => u.alive && u.id !== unit.id).map((u) => `${u.pos.x},${u.pos.y}`)
  );
  const out = [];
  for (let x = 0; x < BOARD_SIZE; x++) {
    for (let y = 0; y < BOARD_SIZE; y++) {
      const dest = { x, y };
      if (engine.cells[y][x] === "HAZARD") continue;
      if (posEq(dest, BOSS_POS)) continue;
      if (occupied.has(`${x},${y}`) && !posEq(dest, unit.pos)) continue;
      if (dist(unit.pos, dest) <= MOVE_RANGE[unit.job]) out.push(dest);
    }
  }
  return out;
}

export function pickMoveDest(unit, engine) {
  const options = reachable(unit, engine);
  if (!options.length) return unit.pos;
  return options.reduce((best, p) => (scorePosition(unit, p, engine) > scorePosition(unit, best, engine) ? p : best));
}

export function pickGcdSkill(unit, engine) {
  if (unit.job === "white_mage") {
    const low = Math.min(...engine.living().map((u) => u.hp / u.maxHp));
    return low < 0.45 ? "medica" : "cure";
  }
  if (unit.job === "black_mage" && !unit.moved) return "fire";
  return JOB_SKILLS[unit.job][0];
}

export function pickGcdTarget(unit, engine) {
  if (unit.job === "white_mage") {
    return [...engine.living()].sort((a, b) => a.hp / a.maxHp - b.hp / b.maxHp)[0].pos;
  }
  return BOSS_POS;
}

export function pickOgcd(unit, engine) {
  if (engine.boss.fury > 0) return ["interrupt", BOSS_POS];
  if (unit.job === "knight" && unit.mit === 0 && engine.boss.phase >= 2) return ["rampart", unit.pos];
  if (unit.job === "white_mage") {
    const low = [...engine.living()].sort((a, b) => a.hp / a.maxHp - b.hp / b.maxHp)[0];
    if (low.hp / low.maxHp < 0.35) return ["benediction", low.pos];
  }
  if (unit.job === "black_mage" && unit.mit === 0) return ["manaward", unit.pos];
  if (unit.job === "bard" && !engine.living().some((u) => u.song > 0)) return ["mages_ballad", unit.pos];
  if (unit.job === "knight" && engine.boss.phase >= 2) return ["provoke", BOSS_POS];
  return null;
}
