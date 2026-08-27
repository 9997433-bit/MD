/** Unified network client: WebSocket preferred, HTTP fallback. */

import { HostClient } from "./hostClient.js";
import { HostWsClient } from "./hostWsClient.js";

export async function createHostClient({ wsUrl, httpUrl, preferWs = true }) {
  if (preferWs && typeof WebSocket !== "undefined") {
    const ws = new HostWsClient(wsUrl);
    try {
      const welcome = await ws.connect();
      return { client: ws, transport: "ws", welcome };
    } catch (err) {
      console.warn("WebSocket failed, falling back to HTTP", err);
    }
  }

  const http = new HostClient(httpUrl);
  const welcome = await http.connect();
  return { client: http, transport: "http", welcome };
}
