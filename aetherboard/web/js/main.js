import { BattleEngine } from "./engine.js";
import { GameUI } from "./ui.js";
import { createHostClient } from "./hostNetClient.js";
import { importHostState } from "./hostState.js";

const params = new URLSearchParams(window.location.search);
const remoteMode = params.get("client") === "1" || params.get("mode") === "client";
const hostUrl = params.get("host") || "http://127.0.0.1:8768";
const wsUrl = params.get("ws") || "ws://127.0.0.1:8769";
const preferWs = params.get("http") !== "1";
const playerId = parseInt(params.get("player") || "1", 10);

let engine = new BattleEngine(42, "earth");

function switchBoss(bossId) {
  engine = new BattleEngine(42, bossId);
  ui.engine = engine;
}

const ui = new GameUI(engine, switchBoss, { remoteMode });
ui.setPlayerId(playerId);

async function initRemote() {
  ui.setStatus("正在连接 Host…");
  try {
    const { client, transport, welcome } = await createHostClient({
      wsUrl,
      httpUrl: hostUrl,
      preferWs,
    });
    client.setPlayerId(playerId);
    client.onState = (payload) => {
      importHostState(engine, payload);
      ui.render();
    };
    ui.setHostClient(client, welcome.coop ?? client.coop);

    if (transport === "http") {
      importHostState(engine, await client.fetchState());
    }

    ui.setStatus(`已连接 (${transport.toUpperCase()}) · P${playerId}${welcome.coop ? " · 双人" : ""}`);
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
