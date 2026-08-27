import { BattleEngine } from "./engine.js";
import { GameUI } from "./ui.js";

let engine = new BattleEngine(42, "earth");

function switchBoss(bossId) {
  engine = new BattleEngine(42, bossId);
  ui.engine = engine;
}

const ui = new GameUI(engine, switchBoss);
ui.render();
