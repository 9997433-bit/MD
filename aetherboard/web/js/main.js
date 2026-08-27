import { BattleEngine } from "./engine.js";
import { GameUI } from "./ui.js";

const engine = new BattleEngine(42);
const ui = new GameUI(engine);
ui.render();
