export const BOARD_SIZE = 7;
export const BOSS_POS = { x: 3, y: 2 };

export const Phase = {
  WARNING: "WARNING",
  MOVE: "MOVE",
  ACTION: "ACTION",
  WEAVE: "WEAVE",
  RESOLVE: "RESOLVE",
  VICTORY: "VICTORY",
  DEFEAT: "DEFEAT",
};

export const CellKind = { NORMAL: "NORMAL", HAZARD: "HAZARD", PREVIEW: "PREVIEW" };

export const Telegraph = {
  NONE: "NONE",
  SLAM: "SLAM",
  EARTHQUAKE: "EARTHQUAKE",
  SHRINK: "SHRINK",
  EARTHEN_FURY: "EARTHEN_FURY",
  GALE: "GALE",
  SPREAD: "SPREAD",
  STACK: "STACK",
  CYCLONE: "CYCLONE",
};

export const SKILLS = {
  shield_bash: { id: "shield_bash", name: "盾击", kind: "gcd", range: 1, power: 80, heal: 0, aoe: 0, mit: 0 },
  rampart: { id: "rampart", name: "铁壁", kind: "ogcd", range: 0, power: 0, heal: 0, aoe: 0, mit: 2 },
  provoke: { id: "provoke", name: "挑衅", kind: "ogcd", range: 7, power: 0, heal: 0, aoe: 0, mit: 0 },
  cure: { id: "cure", name: "治疗", kind: "gcd", range: 7, power: 0, heal: 180, aoe: 0, mit: 0 },
  medica: { id: "medica", name: "医技", kind: "gcd", range: 7, power: 0, heal: 90, aoe: 2, mit: 0 },
  benediction: { id: "benediction", name: "天赐", kind: "ogcd", range: 7, power: 0, heal: 9999, aoe: 0, mit: 0 },
  fire: { id: "fire", name: "火炎", kind: "gcd", range: 7, power: 140, heal: 0, aoe: 0, mit: 0 },
  blizzard: { id: "blizzard", name: "冰结", kind: "gcd", range: 7, power: 70, heal: 0, aoe: 0, mit: 0 },
  manaward: { id: "manaward", name: "魔罩", kind: "ogcd", range: 0, power: 0, heal: 0, aoe: 0, mit: 2 },
  straight_shot: { id: "straight_shot", name: "强力射击", kind: "gcd", range: 7, power: 95, heal: 0, aoe: 0, mit: 0 },
  mages_ballad: { id: "mages_ballad", name: "魔人歌", kind: "ogcd", range: 0, power: 0, heal: 0, aoe: 0, mit: 0 },
  repelling_shot: { id: "repelling_shot", name: "后跃射", kind: "ogcd", range: 7, power: 40, heal: 0, aoe: 0, mit: 0 },
  interrupt: { id: "interrupt", name: "打断", kind: "ogcd", range: 7, power: 0, heal: 0, aoe: 0, mit: 0 },
};

export const JOB_SKILLS = {
  knight: ["shield_bash", "rampart", "provoke"],
  white_mage: ["cure", "medica", "benediction"],
  black_mage: ["fire", "blizzard", "manaward"],
  bard: ["straight_shot", "mages_ballad", "repelling_shot"],
};

export const MOVE_RANGE = { knight: 1, white_mage: 1, black_mage: 1, bard: 2 };

export const TELEGRAPH_TEXT = {
  SLAM: "重击：中心 3×3 受创",
  EARTHQUAKE: "地震：预告区域危险",
  SHRINK: "缩圈：外圈即死",
  EARTHEN_FURY: "土神之怒：2 回合内打断",
  GALE: "风刃：中央列高伤",
  SPREAD: "分散：相邻友军受罚",
  STACK: "集合：必须靠近中心",
  CYCLONE: "旋风：2 回合内打断",
};
