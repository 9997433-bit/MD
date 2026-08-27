import { BattleEngine } from "./engine.js";
import { Phase } from "./constants.js";

function phaseFromString(value) {
  if (!value) return Phase.WARNING;
  return Phase[value] ?? Phase.WARNING;
}

function applyCommand(engine, cmd) {
  const type = cmd.type;
  if (type === "Move") {
    return engine.moveUnit(cmd.unitId, { x: cmd.targetX, y: cmd.targetY });
  }
  if (type === "Skill") {
    const target =
      cmd.targetX >= 0 && cmd.targetY >= 0 ? { x: cmd.targetX, y: cmd.targetY } : null;
    return engine.useSkill(cmd.unitId, cmd.skillId, target);
  }
  if (type === "EndPhase") {
    engine.endPhase();
    return true;
  }
  if (type === "SetBoss") {
    engine.reset(cmd.bossId || "earth");
    return true;
  }
  return false;
}

export class CommandLog {
  constructor(seed = 42, bossId = "earth") {
    this.seed = seed;
    this.bossId = bossId;
    this.commands = [];
  }

  record(cmd) {
    this.commands.push({
      turn: cmd.turn ?? 1,
      phase: cmd.phase ?? Phase.WARNING,
      type: cmd.type,
      unitId: cmd.unitId ?? "",
      skillId: cmd.skillId ?? "",
      targetX: cmd.targetX ?? -1,
      targetY: cmd.targetY ?? -1,
      bossId: cmd.bossId ?? "",
      playerId: cmd.playerId ?? 0,
    });
  }

  toJson() {
    return JSON.stringify({
      seed: this.seed,
      bossId: this.bossId,
      commands: this.commands.map((c) => ({
        turn: c.turn,
        phase: c.phase,
        type: c.type,
        unitId: c.unitId,
        skillId: c.skillId,
        targetX: c.targetX,
        targetY: c.targetY,
        bossId: c.bossId,
      })),
    });
  }

  static fromJson(json) {
    const data = typeof json === "string" ? JSON.parse(json) : json;
    const log = new CommandLog(data.seed ?? 42, data.bossId ?? "earth");
    for (const raw of data.commands ?? []) {
      log.record({
        turn: raw.turn,
        phase: phaseFromString(raw.phase),
        type: raw.type,
        unitId: raw.unitId,
        skillId: raw.skillId,
        targetX: raw.targetX,
        targetY: raw.targetY,
        bossId: raw.bossId,
        playerId: raw.playerId,
      });
    }
    return log;
  }
}

export function replayCommands(log) {
  const engine = new BattleEngine(log.seed, log.bossId);
  engine.beginWarning();
  for (const cmd of log.commands) {
    applyCommand(engine, cmd);
  }
  return engine;
}

export function downloadReplayJson(log, filename = "aetherboard_replay.json") {
  const blob = new Blob([log.toJson()], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
