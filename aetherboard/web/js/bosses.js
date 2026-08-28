import { BOARD_SIZE, BOSS_POS, Telegraph } from "./constants.js";

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

const center = { x: 3, y: 3 };

export const BOSS_PROFILES = {
  earth: {
    id: "earth",
    name: "土灵守护者",
    maxHp: 4200,
    victory: "胜利！土灵守护者被击败。",
    furyName: "土神之怒",
    pickTelegraph(boss) {
      if (boss.phase === 1) return Telegraph.SLAM;
      if (boss.phase === 2) return Telegraph.EARTHQUAKE;
      if (boss.fury > 0) return Telegraph.EARTHEN_FURY;
      if (boss.shrink < 1) return Telegraph.SHRINK;
      return Telegraph.EARTHEN_FURY;
    },
    preview(telegraph, boss, pending) {
      const text = {
        [Telegraph.SLAM]: "重击：中心 3×3 受创",
        [Telegraph.EARTHQUAKE]: "地震：预告区域危险",
        [Telegraph.SHRINK]: "缩圈：外圈即死",
        [Telegraph.EARTHEN_FURY]: "土神之怒：2 回合内打断",
      }[telegraph] || "";
      let danger = pending?.length ? pending : [];
      if (telegraph === Telegraph.SLAM) danger = inRadius(BOSS_POS, 1);
      if (telegraph === Telegraph.SHRINK && boss.shrink < 1) {
        danger = [];
        for (let x = 0; x < BOARD_SIZE; x++) {
          for (let y = 0; y < BOARD_SIZE; y++) {
            if (x === 0 || y === 0 || x === 6 || y === 6) danger.push({ x, y });
          }
        }
      }
      return { text, danger };
    },
    resolve(telegraph, boss, pending, rng) {
      const logs = [];
      let hazards = [];
      if (telegraph === Telegraph.SLAM) {
        hazards = inRadius(BOSS_POS, 1);
        logs.push("重击落下！");
      } else if (telegraph === Telegraph.EARTHQUAKE) {
        hazards = pending || [];
        logs.push("地震爆发！");
      } else if (telegraph === Telegraph.SHRINK) {
        boss.shrink += 1;
        const depth = boss.shrink - 1;
        for (let x = 0; x < BOARD_SIZE; x++) {
          for (let y = 0; y < BOARD_SIZE; y++) {
            if (x <= depth || y <= depth || x >= 6 - depth || y >= 6 - depth) hazards.push({ x, y });
          }
        }
        logs.push("外圈变为即死区！");
      } else if (telegraph === Telegraph.EARTHEN_FURY && boss.fury > 0) {
        boss.fury -= 1;
        if (boss.fury === 0) logs.push("土神之怒发动！");
      }
      const dmg = {
        [Telegraph.SLAM]: 180,
        [Telegraph.EARTHQUAKE]: 130,
        [Telegraph.EARTHEN_FURY]: 9999,
      }[telegraph] || 0;
      return { hazards, logs, dmg, spread: false, stack: false };
    },
    basicDamage(boss) {
      return boss.phase === 1 ? 120 : boss.phase === 2 ? 150 : 180;
    },
  },
  wind: {
    id: "wind",
    name: "风灵领主",
    maxHp: 5000,
    victory: "胜利！风灵领主被击败。",
    furyName: "旋风",
    pickTelegraph(boss) {
      if (boss.phase === 1) return Telegraph.GALE;
      if (boss.phase === 2) return Telegraph.SPREAD;
      if (boss.fury > 0) return Telegraph.CYCLONE;
      return Telegraph.STACK;
    },
    preview(telegraph) {
      const text = {
        [Telegraph.GALE]: "风刃：中央列高伤",
        [Telegraph.SPREAD]: "分散：相邻友军受罚",
        [Telegraph.STACK]: "集合：必须靠近中心",
        [Telegraph.CYCLONE]: "旋风：2 回合内打断",
      }[telegraph] || "";
      let danger = [];
      if (telegraph === Telegraph.GALE) {
        for (let y = 3; y < BOARD_SIZE; y++) danger.push({ x: 3, y });
      }
      if (telegraph === Telegraph.STACK) danger = inRadius(center, 1);
      return { text, danger };
    },
    resolve(telegraph, boss) {
      const logs = [];
      let hazards = [];
      if (telegraph === Telegraph.GALE) {
        for (let y = 3; y < BOARD_SIZE; y++) hazards.push({ x: 3, y });
        logs.push("风刃扫过中央列！");
      } else if (telegraph === Telegraph.SPREAD) logs.push("分散判定！");
      else if (telegraph === Telegraph.STACK) logs.push("集合判定！");
      else if (telegraph === Telegraph.CYCLONE && boss.fury > 0) {
        boss.fury -= 1;
        if (boss.fury === 0) logs.push("旋风发动！");
      }
      const dmg = {
        [Telegraph.GALE]: 150,
        [Telegraph.SPREAD]: 200,
        [Telegraph.STACK]: 220,
        [Telegraph.CYCLONE]: 9999,
      }[telegraph] || 0;
      return {
        hazards,
        logs,
        dmg,
        spread: telegraph === Telegraph.SPREAD,
        stack: telegraph === Telegraph.STACK,
      };
    },
    basicDamage(boss) {
      return boss.phase === 1 ? 100 : boss.phase === 2 ? 130 : 160;
    },
  },
  ice: {
    id: "ice",
    name: "冰灵女皇",
    maxHp: 4800,
    victory: "胜利！冰灵女皇被击败。",
    furyName: "暴雪",
    pickTelegraph(boss) {
      if (boss.phase === 1) return Telegraph.ICE_LANCE;
      if (boss.phase === 2) return Telegraph.FROZEN_GROUND;
      if (boss.fury > 0) return Telegraph.BLIZZARD;
      if (boss.shrink < 1) return Telegraph.ICE_RING;
      return Telegraph.BLIZZARD;
    },
    preview(telegraph, boss, pending) {
      const text = {
        [Telegraph.ICE_LANCE]: "冰枪：十字路径高伤",
        [Telegraph.FROZEN_GROUND]: "霜冻：2×2 危险区",
        [Telegraph.ICE_RING]: "冰环：站在距中心 2 格",
        [Telegraph.BLIZZARD]: "暴雪：2 回合内打断",
      }[telegraph] || "";
      let danger = pending?.length ? pending : [];
      const center = { x: 3, y: 3 };
      if (telegraph === Telegraph.ICE_LANCE) {
        danger = [];
        for (let x = 0; x < BOARD_SIZE; x++) danger.push({ x, y: BOSS_POS.y });
        for (let y = 0; y < BOARD_SIZE; y++) danger.push({ x: BOSS_POS.x, y });
      } else if (telegraph === Telegraph.ICE_RING) {
        danger = [];
        for (let x = 0; x < BOARD_SIZE; x++)
          for (let y = 0; y < BOARD_SIZE; y++) {
            const d = Math.abs(x - center.x) + Math.abs(y - center.y);
            if (d !== 2) danger.push({ x, y });
          }
      }
      return { text, danger };
    },
    resolve(telegraph, boss, pending) {
      const hazards = [];
      const logs = [];
      if (telegraph === Telegraph.ICE_LANCE) {
        for (let x = 0; x < BOARD_SIZE; x++) hazards.push({ x, y: BOSS_POS.y });
        for (let y = 0; y < BOARD_SIZE; y++) hazards.push({ x: BOSS_POS.x, y });
        logs.push("冰枪十字扫过！");
      } else if (telegraph === Telegraph.FROZEN_GROUND) {
        hazards = pending || [];
        logs.push("霜冻爆发！");
      }
      else if (telegraph === Telegraph.ICE_RING) {
        boss.shrink += 1;
        logs.push("冰环判定！");
      } else if (telegraph === Telegraph.BLIZZARD && boss.fury > 0) {
        boss.fury -= 1;
        if (boss.fury === 0) logs.push("暴雪发动！");
      }
      const dmg = {
        [Telegraph.ICE_LANCE]: 160,
        [Telegraph.FROZEN_GROUND]: 140,
        [Telegraph.ICE_RING]: 210,
        [Telegraph.BLIZZARD]: 9999,
      }[telegraph] || 0;
      return {
        hazards,
        logs,
        dmg,
        spread: false,
        stack: false,
        iceRing: telegraph === Telegraph.ICE_RING,
      };
    },
    basicDamage(boss) {
      return boss.phase === 1 ? 110 : boss.phase === 2 ? 140 : 170;
    },
  },
  fire: {
    id: "fire",
    name: "火灵君主",
    maxHp: 5200,
    victory: "胜利！火灵君主被击败。",
    furyName: "喷发",
    pickTelegraph(boss) {
      if (boss.phase === 1) return Telegraph.FLAME_BREATH;
      if (boss.phase === 2) return Telegraph.METEOR;
      if (boss.fury > 0) return Telegraph.ERUPTION;
      if (boss.shrink < 1) return Telegraph.HEAT_LINK;
      return Telegraph.ERUPTION;
    },
    preview(telegraph, boss, pending) {
      const text = {
        [Telegraph.FLAME_BREATH]: "火息：对角线 X 路径",
        [Telegraph.METEOR]: "陨石：随机落点危险",
        [Telegraph.HEAT_LINK]: "灼热连结：必须与友军相邻",
        [Telegraph.ERUPTION]: "喷发：2 回合内打断",
      }[telegraph] || "";
      let danger = pending?.length ? pending : [];
      if (telegraph === Telegraph.FLAME_BREATH) {
        danger = [];
        for (let x = 0; x < BOARD_SIZE; x++)
          for (let y = 0; y < BOARD_SIZE; y++) {
            if (Math.abs(x - center.x) === Math.abs(y - center.y)) danger.push({ x, y });
          }
      }
      return { text, danger };
    },
    resolve(telegraph, boss, pending) {
      const logs = [];
      let hazards = [];
      if (telegraph === Telegraph.FLAME_BREATH) {
        for (let x = 0; x < BOARD_SIZE; x++)
          for (let y = 0; y < BOARD_SIZE; y++) {
            if (Math.abs(x - center.x) === Math.abs(y - center.y)) hazards.push({ x, y });
          }
        logs.push("火息沿对角线扫过！");
      } else if (telegraph === Telegraph.METEOR) {
        hazards = pending || [];
        logs.push("陨石砸落！");
      } else if (telegraph === Telegraph.HEAT_LINK) {
        boss.shrink += 1;
        logs.push("灼热连结判定！");
      } else if (telegraph === Telegraph.ERUPTION && boss.fury > 0) {
        boss.fury -= 1;
        if (boss.fury === 0) logs.push("喷发发动！");
      }
      const dmg = {
        [Telegraph.FLAME_BREATH]: 155,
        [Telegraph.METEOR]: 150,
        [Telegraph.HEAT_LINK]: 200,
        [Telegraph.ERUPTION]: 9999,
      }[telegraph] || 0;
      return {
        hazards,
        logs,
        dmg,
        spread: false,
        stack: false,
        iceRing: false,
        heatLink: telegraph === Telegraph.HEAT_LINK,
      };
    },
    basicDamage(boss) {
      return boss.phase === 1 ? 115 : boss.phase === 2 ? 145 : 175;
    },
  },
};
