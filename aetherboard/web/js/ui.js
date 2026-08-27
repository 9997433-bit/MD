import { BOSS_POS, JOB_SKILLS, Phase, SKILLS, TELEGRAPH_TEXT } from "./constants.js";
import { importHostState } from "./hostState.js";
import { canControl } from "./coop.js";

const phaseLabel = {
  WARNING: "预警",
  MOVE: "移动",
  ACTION: "GCD 行动",
  WEAVE: "oGCD 插入",
  RESOLVE: "结算",
  VICTORY: "胜利",
  DEFEAT: "失败",
};

export class GameUI {
  constructor(engine, onBossChange, options = {}) {
    this.engine = engine;
    this.onBossChange = onBossChange;
    this.remoteMode = options.remoteMode ?? false;
    this.hostClient = null;
    this.coopEnabled = false;
    this.playerId = 1;
    this.selectedUnitId = null;
    this.pendingSkillId = null;

    this.boardEl = document.getElementById("board");
    this.bossNameEl = document.getElementById("boss-name");
    this.turnInfo = document.getElementById("turn-info");
    this.phaseInfo = document.getElementById("phase-info");
    this.telegraphInfo = document.getElementById("telegraph-info");
    this.bossHpBar = document.getElementById("boss-hp-bar");
    this.bossHpText = document.getElementById("boss-hp-text");
    this.bossPhase = document.getElementById("boss-phase");
    this.furyIndicator = document.getElementById("fury-indicator");
    this.partyList = document.getElementById("party-list");
    this.selectedUnit = document.getElementById("selected-unit");
    this.skillButtons = document.getElementById("skill-buttons");
    this.battleLog = document.getElementById("battle-log");
    this.bossSelect = document.getElementById("boss-select");
    this.netStatus = document.getElementById("net-status");

    document.getElementById("btn-end-phase").addEventListener("click", () => this.handleEndPhase());
    document.getElementById("btn-auto").addEventListener("click", () => this.handleAuto());
    document.getElementById("btn-reset").addEventListener("click", () => this.handleReset());
    this.bossSelect.addEventListener("change", () => {
      if (this.remoteMode) return;
      this.onBossChange(this.bossSelect.value);
      this.selectedUnitId = null;
      this.pendingSkillId = null;
      this.render();
    });
  }

  setPlayerId(id) {
    this.playerId = id === 2 ? 2 : 1;
  }

  setHostClient(client, coopEnabled = false) {
    this.hostClient = client;
    this.coopEnabled = coopEnabled;
    this.remoteMode = true;
    this.bossSelect.disabled = true;
    document.getElementById("btn-auto").disabled = true;
    document.getElementById("btn-reset").disabled = true;
    this.netStatus?.classList.remove("hidden");
    if (client.setPlayerId) client.setPlayerId(this.playerId);

    const playerSelect = document.getElementById("player-select");
    if (coopEnabled && playerSelect) {
      playerSelect.classList.remove("hidden");
      const btnP1 = document.getElementById("btn-p1");
      const btnP2 = document.getElementById("btn-p2");
      const syncButtons = () => {
        btnP1?.classList.toggle("active", this.playerId === 1);
        btnP2?.classList.toggle("active", this.playerId === 2);
      };
      btnP1?.addEventListener("click", () => {
        this.playerId = 1;
        client.setPlayerId?.(1);
        syncButtons();
      });
      btnP2?.addEventListener("click", () => {
        this.playerId = 2;
        client.setPlayerId?.(2);
        syncButtons();
      });
      syncButtons();
    }
  }

  setStatus(text) {
    if (this.netStatus) this.netStatus.textContent = text;
  }

  async applyHostPayload(payload) {
    importHostState(this.engine, payload);
  }

  async handleEndPhase() {
    if (this.hostClient) {
      try {
        await this.applyHostPayload(await this.hostClient.endPhase());
      } catch (err) {
        this.setStatus(`命令失败: ${err.message}`);
      }
    } else {
      this.engine.endPhase();
    }
    this.render();
  }

  async handleAuto() {
    if (this.hostClient) return;
    this.engine.stepAuto();
    this.render();
  }

  async handleReset() {
    if (this.hostClient) return;
    this.engine.reset(this.bossSelect.value);
    this.selectedUnitId = null;
    this.pendingSkillId = null;
    this.render();
  }

  render() {
    this.renderBoard();
    this.renderHud();
    this.renderParty();
    this.renderSkills();
    this.renderLog();
  }

  renderHud() {
    const { turn, phase, boss } = this.engine;
    this.bossNameEl.textContent = boss.name;
    this.turnInfo.textContent = `回合 ${turn}`;
    this.phaseInfo.textContent = `阶段：${phaseLabel[phase] || phase}`;
    this.telegraphInfo.textContent = boss.telegraph !== "NONE"
      ? `机制：${TELEGRAPH_TEXT[boss.telegraph] || boss.telegraph}`
      : "—";
    const ratio = boss.hp / boss.maxHp;
    this.bossHpBar.style.width = `${Math.max(0, ratio * 100)}%`;
    this.bossHpText.textContent = `${boss.hp} / ${boss.maxHp}`;
    this.bossPhase.textContent = `Phase ${boss.phase}`;
    this.furyIndicator.classList.toggle("hidden", boss.fury <= 0);
    if (boss.fury > 0) {
      this.furyIndicator.textContent = `${this.engine.profile.furyName}读条：剩余 ${boss.fury} 回合`;
    }
    this.bossSelect.value = this.engine.bossId;
  }

  isPreviewCell(x, y) {
    return (this.engine.previewCells || []).some((p) => p.x === x && p.y === y);
  }

  renderBoard() {
    this.boardEl.innerHTML = "";
    for (let y = 0; y < 7; y++) {
      for (let x = 0; x < 7; x++) {
        const cell = document.createElement("button");
        cell.className = "cell";
        cell.dataset.x = x;
        cell.dataset.y = y;
        if (this.engine.cells[y][x] === "HAZARD") cell.classList.add("hazard");
        if (this.isPreviewCell(x, y)) cell.classList.add("preview");
        if (x === BOSS_POS.x && y === BOSS_POS.y) {
          cell.classList.add("boss-cell");
          const bossToken = document.createElement("div");
          bossToken.className = "boss-token";
          bossToken.textContent = "BOSS";
          cell.appendChild(bossToken);
        }
        const unit = this.engine.party.find((u) => u.pos.x === x && u.pos.y === y);
        if (unit) {
          const token = document.createElement("div");
          token.className = `unit-token ${unit.job}${unit.alive ? "" : " dead"}`;
          token.textContent = unit.name.slice(0, 2);
          cell.appendChild(token);
        }
        cell.addEventListener("click", () => this.onCellClick(x, y));
        this.boardEl.appendChild(cell);
      }
    }
  }

  renderParty() {
    this.partyList.innerHTML = "";
    this.engine.party.forEach((u) => {
      const li = document.createElement("li");
      li.textContent = `${u.name} ${u.hp}/${u.maxHp}${u.alive ? "" : " (倒下)"}`;
      if (u.id === this.selectedUnitId) li.classList.add("selected");
      li.addEventListener("click", () => {
        if (!canControl(this.playerId, u.id, this.coopEnabled)) {
          this.setStatus(`P${this.playerId} 无权控制 ${u.name}`);
          return;
        }
        this.selectedUnitId = u.id;
        this.pendingSkillId = null;
        this.render();
      });
      this.partyList.appendChild(li);
    });
  }

  renderSkills() {
    this.skillButtons.innerHTML = "";
    const unit = this.selectedUnitId ? this.engine.unit(this.selectedUnitId) : null;
    if (!unit || !unit.alive) {
      this.selectedUnit.textContent = "选择单位";
      return;
    }
    this.selectedUnit.textContent = `${unit.name} · 移动${unit.moved ? "✓" : ""} GCD${unit.gcd ? "✓" : ""} oGCD${unit.ogcd ? "✓" : ""}`;

    const skills = [...JOB_SKILLS[unit.job]];
    if (this.engine.boss.fury > 0) skills.push("interrupt");

    skills.forEach((skillId) => {
      const skill = SKILLS[skillId];
      const btn = document.createElement("button");
      btn.className = "skill";
      btn.textContent = `${skill.name} (${skill.kind})`;
      btn.disabled = !this.engine.canUseSkill(unit.id, skillId, skill.heal > 0 ? unit.pos : BOSS_POS);
      btn.addEventListener("click", () => {
        this.pendingSkillId = skillId;
        this.render();
      });
      if (this.pendingSkillId === skillId) btn.style.outline = "2px solid #5eb1ff";
      this.skillButtons.appendChild(btn);
    });
  }

  renderLog() {
    this.battleLog.innerHTML = "";
    [...this.engine.log].reverse().forEach((entry) => {
      const li = document.createElement("li");
      li.textContent = entry;
      this.battleLog.appendChild(li);
    });
  }

  onCellClick(x, y) {
    const dest = { x, y };
    const unit = this.selectedUnitId ? this.engine.unit(this.selectedUnitId) : null;
    if (!unit || !unit.alive) return;

    if (this.pendingSkillId) {
      if (this.hostClient) {
        this.hostClient
          .skill(unit.id, this.pendingSkillId, x, y)
          .then((payload) => {
            this.applyHostPayload(payload);
            this.pendingSkillId = null;
            this.render();
          })
          .catch((err) => this.setStatus(`技能失败: ${err.message}`));
        return;
      }
      const ok = this.engine.useSkill(unit.id, this.pendingSkillId, dest);
      if (ok) this.pendingSkillId = null;
      this.render();
      return;
    }

    if (this.engine.phase === Phase.MOVE) {
      if (this.hostClient) {
        this.hostClient
          .move(unit.id, x, y)
          .then((payload) => {
            this.applyHostPayload(payload);
            this.render();
          })
          .catch((err) => this.setStatus(`移动失败: ${err.message}`));
        return;
      }
      this.engine.moveUnit(unit.id, dest);
      this.render();
    }
  }
}
