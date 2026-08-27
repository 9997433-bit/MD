#!/usr/bin/env python3
"""Authoritative battle host — TCP + HTTP + WebSocket for Unity / Web clients.

Usage:
    cd aetherboard
    pip install -r requirements.txt   # optional, for WebSocket
    PYTHONPATH=. python3 scripts/battle_host.py --coop
"""

from __future__ import annotations

import argparse
import json
import socket
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from sim.battle import BattleEngine
from sim.coop_rules import can_control, command_requires_unit
from sim.state_codec import state_to_dict
from sim.types import Pos


class BattleHost:
    def __init__(self, seed: int = 42, boss_id: str = "earth", coop: bool = False) -> None:
        self.engine = BattleEngine(seed=seed, boss_id=boss_id)
        self.engine.begin_warning()
        self.seed = seed
        self.boss_id = boss_id
        self.coop = coop
        self.lock = threading.Lock()
        self.clients: list[socket.socket] = []
        self._ws_clients: list[Any] = []
        self._ws_loop: Any = None

    def preview_cells(self) -> list[Pos]:
        state = self.engine.state
        if state.pending_hazards:
            return list(state.pending_hazards)
        return self.engine.telegraph_preview()

    def export_state(self) -> dict[str, Any]:
        return state_to_dict(
            self.engine.state,
            self.engine.boss_id,
            preview_cells=self.preview_cells(),
        )

    def apply_command(self, cmd: dict[str, Any]) -> tuple[bool, str | None]:
        ctype = cmd.get("type")
        player_id = int(cmd.get("playerId") or 0)
        unit_id = cmd.get("unitId") or ""

        if self.coop and command_requires_unit(ctype) and not can_control(player_id, unit_id, True):
            return False, f"P{player_id} 无权控制 {unit_id}"

        if ctype == "Move":
            ok = self.engine.move_unit(unit_id, Pos(cmd["targetX"], cmd["targetY"]))
        elif ctype == "Skill":
            target = None
            if cmd.get("targetX", -1) >= 0 and cmd.get("targetY", -1) >= 0:
                target = Pos(cmd["targetX"], cmd["targetY"])
            ok = self.engine.use_skill(unit_id, cmd["skillId"], target)
        elif ctype == "EndPhase":
            self.engine.end_phase()
            ok = True
        elif ctype == "SetBoss":
            self.engine.reset(boss_id=cmd.get("bossId", "earth"))
            ok = True
        else:
            return False, f"Unknown command type: {ctype}"
        if not ok:
            return False, "Command rejected by battle rules."
        return True, None

    def handle_command_envelope(self, envelope: dict[str, Any]) -> tuple[bool, dict[str, Any], str | None]:
        if envelope.get("type") != "command":
            return False, self.export_state(), "Expected command envelope"
        cmd = envelope.get("cmd", {})
        with self.lock:
            ok, err = self.apply_command(cmd)
            state = self.export_state()
        if not ok:
            return False, state, err
        self.broadcast({"type": "state", "payload": state})
        return True, state, None

    def register(self, sock: socket.socket) -> None:
        with self.lock:
            self.clients.append(sock)

    def unregister(self, sock: socket.socket) -> None:
        with self.lock:
            if sock in self.clients:
                self.clients.remove(sock)

    def register_ws(self, ws: Any) -> None:
        with self.lock:
            self._ws_clients.append(ws)

    def unregister_ws(self, ws: Any) -> None:
        with self.lock:
            if ws in self._ws_clients:
                self._ws_clients.remove(ws)

    def set_ws_loop(self, loop: Any) -> None:
        self._ws_loop = loop

    def broadcast(self, message: dict[str, Any]) -> None:
        line = json.dumps(message, ensure_ascii=False) + "\n"
        data = line.encode("utf-8")
        dead: list[socket.socket] = []
        with self.lock:
            for client in self.clients:
                try:
                    client.sendall(data)
                except OSError:
                    dead.append(client)
            for client in dead:
                self.clients.remove(client)

        ws_text = json.dumps(message, ensure_ascii=False)
        self._broadcast_ws(ws_text)

    def _broadcast_ws(self, text: str) -> None:
        import asyncio

        with self.lock:
            clients = list(self._ws_clients)
            loop = self._ws_loop
        if not loop or not clients:
            return

        async def _send_all() -> None:
            dead: list[Any] = []
            for ws in clients:
                try:
                    await ws.send(text)
                except Exception:
                    dead.append(ws)
            if dead:
                with self.lock:
                    for ws in dead:
                        if ws in self._ws_clients:
                            self._ws_clients.remove(ws)

        try:
            asyncio.run_coroutine_threadsafe(_send_all(), loop)
        except RuntimeError:
            pass

    def welcome_message(self) -> dict[str, Any]:
        return {"type": "welcome", "seed": self.seed, "bossId": self.boss_id, "coop": self.coop}


class BattleTCPHandler(socketserver.StreamRequestHandler):
    host: BattleHost

    def handle(self) -> None:
        self.host.register(self.request)
        try:
            self._send(self.host.welcome_message())
            self._send({"type": "state", "payload": self.host.export_state()})

            for line in self.rfile:
                text = line.decode("utf-8").strip()
                if not text:
                    continue
                try:
                    envelope = json.loads(text)
                except json.JSONDecodeError:
                    self._send({"type": "error", "message": "Invalid JSON"})
                    continue
                ok, _, err = self.host.handle_command_envelope(envelope)
                if not ok:
                    self._send({"type": "error", "message": err or "rejected"})
        finally:
            self.host.unregister(self.request)

    def _send(self, message: dict[str, Any]) -> None:
        line = json.dumps(message, ensure_ascii=False) + "\n"
        self.request.sendall(line.encode("utf-8"))


class BattleTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address: tuple[str, int], host: BattleHost) -> None:
        self.battle_host = host
        super().__init__(server_address, BattleTCPHandler)

    def finish_request(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        self.RequestHandlerClass.host = self.battle_host
        super().finish_request(request, client_address)


class BattleHTTPHandler(BaseHTTPRequestHandler):
    battle_host: BattleHost

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/api/state":
            with self.battle_host.lock:
                state = self.battle_host.export_state()
            self._json_response(200, {"type": "state", "payload": state})
            return
        if self.path.rstrip("/") == "/api/health":
            self._json_response(
                200,
                {"ok": True, "bossId": self.battle_host.boss_id, "coop": self.battle_host.coop},
            )
            return
        self._json_response(404, {"type": "error", "message": "Not found"})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/api/command":
            self._json_response(404, {"type": "error", "message": "Not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError:
            self._json_response(400, {"type": "error", "message": "Invalid JSON"})
            return
        ok, state, err = self.battle_host.handle_command_envelope(envelope)
        if not ok:
            self._json_response(400, {"type": "error", "message": err or "rejected", "payload": state})
            return
        self._json_response(200, {"type": "state", "payload": state})


class BattleHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], host: BattleHost) -> None:
        self.battle_host = host
        super().__init__(server_address, BattleHTTPHandler)

    def finish_request(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        self.RequestHandlerClass.battle_host = self.battle_host
        super().finish_request(request, client_address)


def start_websocket_server(bind_host: str, port: int, battle_host: BattleHost) -> bool:
    try:
        import asyncio
        import websockets
    except ImportError:
        print("WebSocket disabled: pip install websockets")
        return False

    async def handler(websocket: Any) -> None:
        battle_host.register_ws(websocket)
        try:
            await websocket.send(json.dumps(battle_host.welcome_message(), ensure_ascii=False))
            await websocket.send(
                json.dumps({"type": "state", "payload": battle_host.export_state()}, ensure_ascii=False)
            )
            async for message in websocket:
                try:
                    envelope = json.loads(message)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
                    continue
                ok, _, err = battle_host.handle_command_envelope(envelope)
                if not ok:
                    await websocket.send(
                        json.dumps({"type": "error", "message": err or "rejected"}, ensure_ascii=False)
                    )
        finally:
            battle_host.unregister_ws(websocket)

    async def serve() -> None:
        battle_host.set_ws_loop(asyncio.get_running_loop())
        async with websockets.serve(handler, bind_host, port):
            await asyncio.Future()

    def run_loop() -> None:
        asyncio.run(serve())

    threading.Thread(target=run_loop, daemon=True).start()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Aetherboard authoritative battle host")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8767, help="TCP port (Unity)")
    parser.add_argument("--http-port", type=int, default=8768, help="HTTP port (Web fallback)")
    parser.add_argument("--ws-port", type=int, default=8769, help="WebSocket port (Web preferred)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--boss", default="earth", choices=["earth", "wind"])
    parser.add_argument("--coop", action="store_true", help="Enforce P1/P2 unit ownership")
    args = parser.parse_args()

    battle_host = BattleHost(seed=args.seed, boss_id=args.boss, coop=args.coop)

    http_server = BattleHTTPServer((args.host, args.http_port), battle_host)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()

    ws_ok = start_websocket_server(args.host, args.ws_port, battle_host)

    tcp_server = BattleTCPServer((args.host, args.port), battle_host)
    parts = [
        f"TCP {args.host}:{args.port}",
        f"HTTP {args.host}:{args.http_port}",
    ]
    if ws_ok:
        parts.append(f"WS {args.host}:{args.ws_port}")
    print(
        f"Aetherboard host: {' | '.join(parts)} "
        f"(boss={args.boss}, seed={args.seed}, coop={args.coop})"
    )
    try:
        tcp_server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down host.")
        tcp_server.shutdown()
        http_server.shutdown()


if __name__ == "__main__":
    main()
