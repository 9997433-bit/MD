/** HTTP client for Python battle_host (browser-friendly). */

export class HostClient {
  constructor(baseUrl = "http://127.0.0.1:8768") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.connected = false;
  }

  async connect() {
    const res = await fetch(`${this.baseUrl}/api/health`);
    if (!res.ok) throw new Error(`Host unreachable (${res.status})`);
    this.connected = true;
    return res.json();
  }

  async fetchState() {
    const res = await fetch(`${this.baseUrl}/api/state`);
    if (!res.ok) throw new Error(`State fetch failed (${res.status})`);
    const data = await res.json();
    return data.payload;
  }

  async sendCommand(cmd) {
    const res = await fetch(`${this.baseUrl}/api/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "command", cmd }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Command rejected");
    return data.payload;
  }

  async move(unitId, x, y) {
    return this.sendCommand({ type: "Move", unitId, skillId: "", targetX: x, targetY: y, bossId: "" });
  }

  async skill(unitId, skillId, x, y) {
    return this.sendCommand({
      type: "Skill",
      unitId,
      skillId,
      targetX: x ?? -1,
      targetY: y ?? -1,
      bossId: "",
    });
  }

  async endPhase() {
    return this.sendCommand({ type: "EndPhase", unitId: "", skillId: "", targetX: -1, targetY: -1, bossId: "" });
  }
}
