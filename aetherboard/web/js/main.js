import { BattleEngine } from "./engine.js";
import { GameUI } from "./ui.js";
import { HostClient } from "./hostClient.js";
import { importHostState } from "./hostState.js";

const params = new URLSearchParams(window.location.search);
const remoteMode = params.get("client") === "1" || params.get("mode") === "client";
const hostUrl = params.get("host") || "http://127.0.0.1:8768";

let engine = new BattleEngine(42, "earth");
let hostClient = null;

function switchBoss(bossId) {
  if (hostClient) return;
  engine = new BattleEngine(42, bossId);
  ui.engine = engine;
}

const ui = new GameUI(engine, switchBoss, { remoteMode });

async function initRemote() {
  hostClient = new HostClient(hostUrl);
  ui.setHostClient(hostClient);
  ui.setStatus("正在连接 Host…");
  try {
    await hostClient.connect();
    const state = await hostClient.fetchState();
    importHostState(engine, state);
    ui.setStatus(`已连接 Host · ${hostUrl}`);
    ui.render();
  } catch (err) {
    ui.setStatus(`连接失败: ${err.message}`);
    console.error(err);
  }
}

if (remoteMode) {
  initRemote();
} else {
  ui.render();
}
