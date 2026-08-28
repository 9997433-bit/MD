import {
  BOARD_SIZE,
  BOSS_POS,
  CellKind,
  Phase,
  SKILLS,
  Telegraph,
} from "./constants.js";
import { BOSS_PROFILES } from "./bosses.js";
import { pickGcdSkill, pickGcdTarget, pickMoveDest, pickOgcd } from "./ai.js";

function posEq(a, b) {
  return a.x === b.x && a.y === b.y;
}

function dist(a, b) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
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

function makeBoard() {
  return Array.from({ length: BOARD_SIZE }, () =>
    Array.from({ length: BOARD_SIZE }, () => CellKind.NORMAL)
  );
}

function createParty() {
  return [
    { id: "knight", name: "铁卫", job: "knight", pos: { x: 3, y: 5 }, hp: 1200, maxHp: 1200, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
    { id: "white_mage", name: "白愈", job: "white_mage", pos: { x: 2, y: 5 }, hp: 900, maxHp: 900, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
    { id: "black_mage", name: "黑炎", job: "black_mage", pos: { x: 4, y: 5 }, hp: 800, maxHp: 800, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
    { id: "bard", name: "游弦", job: "bard", pos: { x: 3, y: 4 }, hp: 850, maxHp: 850, alive: true, moved: false, gcd: false, ogcd: false, mit: 0, song: 0, taunt: 0 },
  ];
}

export class BattleEngine {
  constructor(seed = 42, bossId = "earth") {
    this.seed = seed;
    this.rngState = seed;
    this.bossId = bossId;
    this.profile = BOSS_PROFILES[bossId] || BOSS_PROFILES.earth;
    this.reset();
  }

  rand() {
    this.rngState = (this.rngState * 16807) % 2147483647;
    return (this.rngState - 1) / 2147483646;
  }

  randInt(min, max) {
    return Math.floor(this.rand() * (max - min + 1)) + min;
  }

  reset(bossId = this.bossId) {
    this.bossId = bossId;
    this.profile = BOSS_PROFILES[bossId] || BOSS_PROFILES.earth;
    this.turn = 1;
    this.phase = Phase.WARNING;
    this.cells = makeBoard();
    this.party = createParty();
    this.boss = {
      name: this.profile.name,
      hp: this.profile.maxHp,
      maxHp: this.profile.maxHp,
      phase: 1,
      telegraph: Telegraph.NONE,
      fury: 0,
      shrink: 0,
      alive: true,
    };
    this.log = [];
    this.pendingHazards = [];
    this.previewCells = [];
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
    if (this.log.length > 100) this.log.shift();
  }

  updateBossPhase() {
    const ratio = this.boss.hp / this.boss.maxHp;
    if (ratio <= 0.4) this.boss.phase = 3;
    else if (ratio <= 0.7) this.boss.phase = 2;
    else this.boss.phase = 1;
  }

  rollPendingHazards(telegraph) {
    if (telegraph === Telegraph.EARTHQUAKE) {
      const center = { x: this.randInt(1, 5), y: this.randInt(1, 5) };
      return inRadius(center, 1);
    }
    if (telegraph === Telegraph.FROZEN_GROUND) {
      const topLeft = { x: this.randInt(1, BOARD_SIZE - 3), y: this.randInt(1, BOARD_SIZE - 3) };
      const out = [];
      for (let dx = 0; dx < 2; dx++) {
        for (let dy = 0; dy < 2; dy++) {
          out.push({ x: topLeft.x + dx, y: topLeft.y + dy });
        }
      }
      return out;
    }
    if (telegraph === Telegraph.METEOR) {
      const picks = [];
      let attempts = 0;
      while (picks.length < 3 && attempts < 40) {
        attempts += 1;
        const c = { x: this.randInt(0, BOARD_SIZE - 1), y: this.randInt(0, BOARD_SIZE - 1) };
        if (posEq(c, BOSS_POS) || picks.some((p) => posEq(p, c))) continue;
        picks.push(c);
      }
      return picks;
    }
    return this.profile.preview(telegraph, this.boss, []).danger;
  }

  beginWarning() {
    if (this.phase === Phase.VICTORY || this.phase === Phase.DEFEAT) return;
    this.updateBossPhase();
    const telegraph = this.profile.pickTelegraph(this.boss);
    this.boss.telegraph = telegraph;
    if ([Telegraph.EARTHEN_FURY, Telegraph.CYCLONE, Telegraph.BLIZZARD, Telegraph.ERUPTION].includes(telegraph) && this.boss.fury === 0) {
      this.boss.fury = 2;
    }
    this.pendingHazards = this.rollPendingHazards(telegraph);
    const preview = this.profile.preview(telegraph, this.boss, this.pendingHazards);
    this.previewCells = preview.danger;
    if (preview.text) this.addLog(`[预警] ${preview.text}`);
    if (telegraph === Telegraph.EARTHQUAKE && this.pendingHazards.length) {
      const c = this.pendingHazards[Math.floor(this.pendingHazards.length / 2)];
      this.addLog(`[预警] 地震中心约在 (${c.x}, ${c.y})。`);
    }
    if (telegraph === Telegraph.FROZEN_GROUND && this.pendingHazards.length) {
      const c = this.pendingHazards[0];
      this.addLog(`[预警] 霜冻区域约在 (${c.x}, ${c.y}) 附近。`);
    }
    if (telegraph === Telegraph.METEOR && this.pendingHazards.length) {
      const spots = this.pendingHazards.slice(0, 3).map((p) => `(${p.x},${p.y})`).join(", ");
      this.addLog(`[预警] 陨石落点约在 ${spots}。`);
    }
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
    const MOVE_RANGE = { knight: 1, white_mage: 1, black_mage: 1, bard: 2 };
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
    if (skillId === "interrupt") {
      return this.phase === Phase.WEAVE && !u.ogcd && this.boss.fury > 0;
    }
    if (skill.kind === "gcd") {
      if (this.phase !== Phase.ACTION || u.gcd) return false;
    } else if (this.phase !== Phase.WEAVE || u.ogcd) {
      return false;
    }
    const allowed = { knight: ["shield_bash", "rampart", "provoke"], white_mage: ["cure", "medica", "benediction"], black_mage: ["fire", "blizzard", "manaward"], bard: ["straight_shot", "mages_ballad", "repelling_shot"] }[u.job];
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
      this.boss.fury = -1;
      this.addLog(`${u.name} 打断了${this.profile.furyName}！`);
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
      this.addLog(this.profile.victory);
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
      }
    }
  }

  hitUnit(unit, raw) {
    const dmg = unit.mit > 0 ? Math.floor(raw * 0.6) : raw;
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

  autoFill() {
    if (this.phase === Phase.WEAVE && this.boss.fury > 0) {
      const knight = this.living().find((u) => u.job === "knight" && !u.ogcd);
      if (knight) this.useSkill(knight.id, "interrupt", BOSS_POS);
    }
    for (const unit of this.living()) {
      if (this.phase === Phase.MOVE && !unit.moved) {
        const dest = pickMoveDest(unit, this);
        if (!posEq(dest, unit.pos)) this.moveUnit(unit.id, dest);
        else unit.moved = true;
      } else if (this.phase === Phase.ACTION && !unit.gcd) {
        this.useSkill(unit.id, pickGcdSkill(unit, this), pickGcdTarget(unit, this));
      } else if (this.phase === Phase.WEAVE && !unit.ogcd) {
        const choice = pickOgcd(unit, this);
        if (choice) this.useSkill(unit.id, choice[0], choice[1]);
      }
    }
  }

  endPhase() {
    if (this.phase === Phase.VICTORY || this.phase === Phase.DEFEAT) return;
    if (this.phase === Phase.MOVE) {
      this.autoFill();
      this.phase = Phase.ACTION;
    } else if (this.phase === Phase.ACTION) {
      this.autoFill();
      this.phase = Phase.WEAVE;
    } else if (this.phase === Phase.WEAVE) {
      this.autoFill();
      this.resolveTurn();
    }
  }

  resolveTurn() {
    const telegraph = this.boss.telegraph;
    this.clearHazards();
    const result = this.profile.resolve(telegraph, this.boss, this.pendingHazards, this);
    result.logs.forEach((l) => this.addLog(l));

    const persist = [Telegraph.SHRINK, Telegraph.EARTHQUAKE, Telegraph.FROZEN_GROUND, Telegraph.METEOR];
    if (result.hazards?.length && persist.includes(telegraph)) {
      this.applyHazards(result.hazards);
      if (result.dmg > 0) {
        this.living().forEach((u) => {
          if (result.hazards.some((h) => posEq(h, u.pos))) this.hitUnit(u, result.dmg);
        });
      }
    } else if (result.dmg > 0 && result.hazards?.length) {
      this.living().forEach((u) => {
        if (result.hazards.some((h) => posEq(h, u.pos))) this.hitUnit(u, result.dmg);
      });
    }

    if ([Telegraph.EARTHEN_FURY, Telegraph.CYCLONE, Telegraph.BLIZZARD, Telegraph.ERUPTION].includes(telegraph) && this.boss.fury === 0) {
      this.living().forEach((u) => this.hitUnit(u, result.dmg));
    }

    if (result.iceRing) {
      const center = { x: 3, y: 3 };
      this.living().forEach((u) => {
        if (dist(u.pos, center) !== 2) this.hitUnit(u, result.dmg);
      });
    }

    if (result.heatLink) {
      const living = this.living();
      living.forEach((u) => {
        if (!living.some((o) => o.id !== u.id && dist(u.pos, o.pos) <= 1)) this.hitUnit(u, result.dmg);
      });
    }

    if (result.spread) {
      const living = this.living();
      const hit = new Set();
      for (let i = 0; i < living.length; i++) {
        for (let j = i + 1; j < living.length; j++) {
          if (dist(living[i].pos, living[j].pos) <= 1) {
            hit.add(living[i].id);
            hit.add(living[j].id);
          }
        }
      }
      living.forEach((u) => { if (hit.has(u.id)) this.hitUnit(u, result.dmg); });
    }
    if (result.stack) {
      const center = { x: 3, y: 3 };
      this.living().forEach((u) => {
        if (dist(u.pos, center) > 1) this.hitUnit(u, result.dmg);
      });
    }

    const tank = this.living().find((u) => u.job === "knight");
    if (this.living().length) {
      const target = tank && tank.taunt > 0 ? tank : this.living()[Math.floor(this.rand() * this.living().length)];
      this.hitUnit(target, this.profile.basicDamage(this.boss));
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
    this.previewCells = [];
    this.beginWarning();
  }

  stepAuto() {
    if (this.phase === Phase.MOVE) {
      this.autoFill();
      this.phase = Phase.ACTION;
    }
    if (this.phase === Phase.ACTION) {
      this.autoFill();
      this.phase = Phase.WEAVE;
    }
    if (this.phase === Phase.WEAVE) {
      this.autoFill();
      this.resolveTurn();
    }
  }
}
