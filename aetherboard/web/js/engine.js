import {
  BOARD_SIZE,
  BOSS_POS,
  CellKind,
  JOB_SKILLS,
  MOVE_RANGE,
  Phase,
  SKILLS,
  Telegraph,
  TELEGRAPH_TEXT,
} from "./constants.js";

function posEq(a, b) {
  return a.x === b.x && a.y === b.y;
}

function dist(a, b) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function makeBoard() {
  return Array.from({ length: BOARD_SIZE }, () =>
    Array.from({ length: BOARD_SIZE }, () => CellKind.NORMAL)
  );
}

function createParty() {
  return [
    { id: "knight", name: "铁卫", job: "knight", pos: { x: 3, y: 5 }, hp: 1200, maxHp: 1200, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
    { id: "white_mage", name: "白愈", job: "white_mage", pos: { x: 2, y: 6 }, hp: 900, maxHp: 900, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
    { id: "black_mage", name: "黑炎", job: "black_mage", pos: { x: 4, y: 6 }, hp: 800, maxHp: 800, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
    { id: "bard", name: "游弦", job: "bard", pos: { x: 3, y: 6 }, hp: 850, maxHp: 850, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
  ];
}

function ringPositions(shrinkLevel) {
  if (shrinkLevel <= 0) return [];
  const depth = shrinkLevel - 1;
  const out = [];
  for (let x = 0; x < BOARD_SIZE; x++) {
    for (let y = 0; y < BOARD_SIZE; y++) {
      if (x <= depth || y <= depth || x >= BOARD_SIZE - 1 - depth || y >= BOARD_SIZE - 1 - depth) {
        out.push({ x, y });
      }
    }
  }
  return out;
}

function inRadius(center, radius) {
  const out = [];
  for (let x = 0; x < BOARD_SIZE; x++) {
    for (let y = 0; y < BOARD_SIZE; y++) {
      if (dist(center, { x, y }) <= radius) out.push({ x, y });
    }
  }
  return out;
}

export class BattleEngine {
  constructor(seed = 7) {
    this.seed = seed;
    this.rngState = seed;
    this.reset();
  }

  rand() {
    this.rngState = (this.rngState * 16807) % 2147483647;
    return (this.rngState - 1) / 2147483646;
  }

  randInt(min, max) {
    return Math.floor(this.rand() * (max - min + 1)) + min;
  }

  reset() {
    this.turn = 1;
    this.phase = Phase.WARNING;
    this.cells = makeBoard();
    this.party = createParty();
    this.boss = { name: "土灵守护者", hp: 6000, maxHp: 6000, phase: 1, telegraph: Telegraph.NONE, fury: 0, shrink: 0, alive: true };
    this.log = [];
    this.pendingSkill = null;
    this.beginWarning();
  }

  living() {
    return this.party.filter((u) => u.alive);
  }

  unit(id) {
    return this.party.find((u) => u.id === id);
  }

  addLog(msg) {
    this.log.push(msg);
    if (this.log.length > 80) this.log.shift();
  }

  updateBossPhase() {
    const ratio = this.boss.hp / this.boss.maxHp;
    if (ratio <= 0.4) this.boss.phase = 3;
    else if (ratio <= 0.7) this.boss.phase = 2;
    else this.boss.phase = 1;
  }

  pickTelegraph() {
    if (this.boss.phase === 1) return Telegraph.SLAM;
    if (this.boss.phase === 2) return Telegraph.EARTHQUAKE;
    if (this.boss.fury > 0) return Telegraph.EARTHEN_FURY;
    if (this.boss.shrink < 1) return Telegraph.SHRINK;
    return Telegraph.EARTHEN_FURY;
  }

  beginWarning() {
    if (this.phase === Phase.VICTORY || this.phase === Phase.DEFEAT) return;
    this.updateBossPhase();
    const telegraph = this.pickTelegraph();
    this.boss.telegraph = telegraph;
    if (telegraph === Telegraph.EARTHEN_FURY && this.boss.fury === 0) this.boss.fury = 2;
    const text = TELEGRAPH_TEXT[telegraph];
    if (text) this.addLog(`[预警] ${text}`);
    this.phase = Phase.MOVE;
  }

  isDeadly(pos) {
    return this.cells[pos.y][pos.x] === CellKind.HAZARD;
  }

  canMove(unitId, dest) {
    const u = this.unit(unitId);
    if (!u || !u.alive || u.moved || this.phase !== Phase.MOVE) return false;
    if (dest.x < 0 || dest.y < 0 || dest.x >= BOARD_SIZE || dest.y >= BOARD_SIZE) return false;
    if (this.isDeadly(dest)) return false;
    if (posEq(dest, u.pos)) return false;
    if (this.party.some((p) => p.alive && p.id !== unitId && posEq(p.pos, dest))) return false;
    if (posEq(dest, BOSS_POS)) return false;
    return dist(u.pos, dest) <= MOVE_RANGE[u.job];
  }

  moveUnit(unitId, dest) {
    if (!this.canMove(unitId, dest)) return false;
    const u = this.unit(unitId);
    u.pos = { ...dest };
    u.moved = true;
    this.addLog(`${u.name} 移动到 (${dest.x}, ${dest.y})`);
    return true;
  }

  dmgMultiplier() {
    return this.party.some((u) => u.alive && u.song > 0) ? 1.2 : 1;
  }

  canUseSkill(unitId, skillId, target) {
    const u = this.unit(unitId);
    const skill = SKILLS[skillId];
    if (!u || !u.alive || !skill) return false;
    if (skill.kind === "gcd") {
      if (this.phase !== Phase.ACTION || u.gcd) return false;
    } else if (this.phase !== Phase.WEAVE || u.ogcd) {
      return false;
    }
    if (skillId === "interrupt") return this.boss.fury > 0;
    const allowed = JOB_SKILLS[u.job] || [];
    if (!allowed.includes(skillId)) return false;
    if (skill.range === 0) return true;
    if (!target) return false;
    if (skill.heal > 0) return this.party.some((p) => p.alive && posEq(p.pos, target));
    return true;
  }

  useSkill(unitId, skillId, target = null) {
    if (!this.canUseSkill(unitId, skillId, target)) return false;
    const u = this.unit(unitId);
    const skill = SKILLS[skillId];
    if (skill.kind === "gcd") u.gcd = true;
    else u.ogcd = true;

    if (skill.heal > 0 && target) {
      const targets = skill.aoe > 0
        ? this.living().filter((p) => dist(p.pos, target) <= skill.aoe)
        : this.living().filter((p) => posEq(p.pos, target));
      targets.forEach((t) => {
        t.hp = skill.heal >= 9999 ? t.maxHp : Math.min(t.maxHp, t.hp + skill.heal);
      });
      this.addLog(`${u.name} 使用 ${skill.name}`);
    } else if (skillId === "interrupt") {
      this.boss.fury = 0;
      this.addLog(`${u.name} 打断了土神之怒！`);
    } else if (skill.mit > 0) {
      u.mit = skill.mit;
      this.addLog(`${u.name} 获得减伤`);
    } else if (skillId === "provoke") {
      u.taunt = 1;
      this.addLog(`${u.name} 挑衅 Boss`);
    } else if (skillId === "mages_ballad") {
      this.living().forEach((p) => { p.song = 3; });
      this.addLog(`${u.name} 开启魔人歌`);
    } else if (skillId === "repelling_shot") {
      this.applyBossDamage(u, skill.power);
      this.repel(u);
    } else {
      this.applyBossDamage(u, skill.power, skillId);
    }

    if (this.boss.hp <= 0) {
      this.boss.alive = false;
      this.phase = Phase.VICTORY;
      this.addLog("胜利！土灵守护者被击败。");
    }
    return true;
  }

  applyBossDamage(unit, basePower, skillId = "") {
    let power = basePower;
    const mult = this.dmgMultiplier();
    if (unit.job === "black_mage" && skillId === "fire" && !unit.moved) {
      power = Math.floor(power * 1.5);
      this.addLog(`${unit.name} 站桩读条，火炎强化`);
    }
    if (unit.job === "bard" && skillId === "straight_shot" && unit.song > 0) {
      power = Math.floor(power * 1.3);
    }
    const dmg = Math.floor(power * mult);
    this.boss.hp = Math.max(0, this.boss.hp - dmg);
    this.addLog(`${unit.name} 使用 ${SKILLS[skillId]?.name || "攻击"}，造成 ${dmg} 伤害`);
  }

  repel(unit) {
    const dx = unit.pos.x - BOSS_POS.x;
    const dy = unit.pos.y - BOSS_POS.y;
    const stepX = dx === 0 ? 0 : dx > 0 ? 1 : -1;
    const stepY = dy === 0 ? 1 : dy > 0 ? 1 : -1;
    const dest = { x: unit.pos.x + stepX, y: unit.pos.y + stepY };
    if (dest.x >= 0 && dest.y >= 0 && dest.x < BOARD_SIZE && dest.y < BOARD_SIZE && !this.isDeadly(dest)) {
      if (!this.party.some((p) => p.alive && p.id !== unit.id && posEq(p.pos, dest))) {
        unit.pos = dest;
        this.addLog(`${unit.name} 后跃`);
      }
    }
  }

  hitUnit(unit, raw) {
    let dmg = unit.mit > 0 ? Math.floor(raw * 0.6) : raw;
    unit.hp = Math.max(0, unit.hp - dmg);
    if (unit.hp === 0) {
      unit.alive = false;
      this.addLog(`${unit.name} 倒下了`);
    }
  }

  clearHazards() {
    for (let y = 0; y < BOARD_SIZE; y++) {
      for (let x = 0; x < BOARD_SIZE; x++) {
        if (this.cells[y][x] === CellKind.HAZARD) this.cells[y][x] = CellKind.NORMAL;
      }
    }
  }

  applyHazards(list) {
    list.forEach((p) => { this.cells[p.y][p.x] = CellKind.HAZARD; });
  }

  endPhase() {
    if (this.phase === Phase.VICTORY || this.phase === Phase.DEFEAT) return;
    if (this.phase === Phase.MOVE) {
      this.living().forEach((u) => { if (!u.moved) u.moved = true; });
      this.phase = Phase.ACTION;
    } else if (this.phase === Phase.ACTION) {
      this.living().forEach((u) => {
        if (!u.gcd) this.useSkill(u.id, JOB_SKILLS[u.job][0], u.job === "white_mage" ? u.pos : BOSS_POS);
      });
      this.phase = Phase.WEAVE;
    } else if (this.phase === Phase.WEAVE) {
      this.resolveTurn();
    }
  }

  resolveTurn() {
    const telegraph = this.boss.telegraph;
    this.clearHazards();

    if (telegraph === Telegraph.SLAM) {
      inRadius(BOSS_POS, 1).forEach((pos) => {
        this.living().forEach((u) => { if (posEq(u.pos, pos)) this.hitUnit(u, 220); });
      });
    } else if (telegraph === Telegraph.EARTHQUAKE) {
      const center = { x: this.randInt(1, 5), y: this.randInt(1, 5) };
      const hazards = inRadius(center, 1);
      this.applyHazards(hazards);
      this.living().forEach((u) => { if (hazards.some((h) => posEq(h, u.pos))) this.hitUnit(u, 160); });
    } else if (telegraph === Telegraph.SHRINK) {
      this.boss.shrink += 1;
      this.applyHazards(ringPositions(this.boss.shrink));
      this.addLog("外圈变为即死区！");
    } else if (telegraph === Telegraph.EARTHEN_FURY && this.boss.fury > 0) {
      this.boss.fury -= 1;
      if (this.boss.fury === 0) {
        this.living().forEach((u) => this.hitUnit(u, 9999));
        this.addLog("土神之怒发动！");
      }
    }

    const tank = this.living().find((u) => u.job === "knight");
    const target = tank && tank.taunt > 0 ? tank : this.living()[Math.floor(this.rand() * this.living().length)];
    if (target) {
      const base = this.boss.phase === 1 ? 140 : this.boss.phase === 2 ? 180 : 220;
      this.hitUnit(target, base);
      this.addLog(`Boss 攻击 ${target.name}`);
    }

    this.living().forEach((u) => {
      if (this.isDeadly(u.pos)) {
        u.alive = false;
        u.hp = 0;
        this.addLog(`${u.name} 站在即死区被淘汰`);
      }
    });

    this.party.forEach((u) => {
      u.moved = false;
      u.gcd = false;
      u.ogcd = false;
      if (u.mit > 0) u.mit -= 1;
      if (u.taunt > 0) u.taunt -= 1;
      if (u.song > 0) u.song -= 1;
    });

    if (!this.living().length) {
      this.phase = Phase.DEFEAT;
      this.addLog("全队阵亡，战斗失败");
      return;
    }
    if (!this.boss.alive) {
      this.phase = Phase.VICTORY;
      return;
    }

    this.turn += 1;
    this.boss.telegraph = Telegraph.NONE;
    this.phase = Phase.RESOLVE;
    this.beginWarning();
  }

  stepAuto() {
    if (this.phase === Phase.MOVE) {
      this.living().forEach((u) => { if (!u.moved) u.moved = true; });
      this.phase = Phase.ACTION;
    }
    if (this.phase === Phase.ACTION) {
      this.living().forEach((u) => {
        if (!u.gcd) {
          if (u.job === "white_mage") {
            const wounded = [...this.living()].sort((a, b) => a.hp / a.maxHp - b.hp / b.maxHp)[0];
            this.useSkill(u.id, "cure", wounded.pos);
          } else {
            this.useSkill(u.id, JOB_SKILLS[u.job][0], BOSS_POS);
          }
        }
      });
      this.phase = Phase.WEAVE;
    }
    if (this.phase === Phase.WEAVE) {
      if (this.boss.fury > 0) {
        const interrupter = this.living().find((u) => u.job === "knight") || this.living()[0];
        if (interrupter) this.useSkill(interrupter.id, "interrupt", BOSS_POS);
      }
      this.resolveTurn();
    }
  }
}
