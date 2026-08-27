/** WebSocket client — preferred for browser multiplayer (push state updates). */

export class HostWsClient {
  constructor(wsUrl = "ws://127.0.0.1:8769") {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.playerId = 1;
    this.coop = false;
    this._pending = null;
    this.onState = null;
    this.onStatus = null;
  }

  setPlayerId(id) {
    this.playerId = id;
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      let welcome = null;

      this.ws.onopen = () => this._emitStatus(`已连接 ${this.wsUrl}`);
      this.ws.onerror = () => reject(new Error("WebSocket 连接失败"));
      this.ws.onclose = () => this._emitStatus("连接已断开");

      this.ws.onmessage = (ev) => {
        let msg;
        try {
          msg = JSON.parse(ev.data);
        } catch {
          return;
        }

        if (msg.type === "welcome") {
          welcome = msg;
          this.coop = !!msg.coop;
          return;
        }

        if (msg.type === "state" && msg.payload) {
          if (welcome) {
            resolve(welcome);
            welcome = null;
          }
          if (this.onState) this.onState(msg.payload);
          if (this._pending) {
            this._pending.resolve(msg.payload);
            this._pending = null;
          }
          return;
        }

        if (msg.type === "error") {
          const err = new Error(msg.message || "rejected");
          if (this._pending) {
            this._pending.reject(err);
            this._pending = null;
          }
        }
      };
    });
  }

  async fetchState() {
    return new Promise((resolve, reject) => {
      this._pending = { resolve, reject };
      setTimeout(() => {
        if (this._pending) {
          this._pending.reject(new Error("State timeout"));
          this._pending = null;
        }
      }, 8000);
    });
  }

  sendCommand(cmd) {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error("未连接"));
        return;
      }
      this._pending = { resolve, reject };
      setTimeout(() => {
        if (this._pending) {
          this._pending.reject(new Error("Command timeout"));
          this._pending = null;
        }
      }, 8000);
      this.ws.send(
        JSON.stringify({
          type: "command",
          cmd: { ...cmd, playerId: this.playerId },
        })
      );
    });
  }

  move(unitId, x, y) {
    return this.sendCommand({ type: "Move", unitId, skillId: "", targetX: x, targetY: y, bossId: "" });
  }

  skill(unitId, skillId, x, y) {
    return this.sendCommand({
      type: "Skill",
      unitId,
      skillId,
      targetX: x ?? -1,
      targetY: y ?? -1,
      bossId: "",
    });
  }

  endPhase() {
    return this.sendCommand({ type: "EndPhase", unitId: "", skillId: "", targetX: -1, targetY: -1, bossId: "" });
  }

  _emitStatus(text) {
    if (this.onStatus) this.onStatus(text);
  }
}
