#!/usr/bin/env python3
"""Authoritative battle host — TCP + HTTP API for Unity / Web clients.

Usage:
    cd aetherboard
    PYTHONPATH=. python3 scripts/battle_host.py --port 8767 --http-port 8768
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
from sim.state_codec import state_to_dict
from sim.types import Pos


class BattleHost:
    def __init__(self, seed: int = 42, boss_id: str = "earth") -> None:
        self.engine = BattleEngine(seed=seed, boss_id=boss_id)
        self.engine.begin_warning()
        self.seed = seed
        self.boss_id = boss_id
        self.lock = threading.Lock()
        self.clients: list[socket.socket] = []

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
        if ctype == "Move":
            ok = self.engine.move_unit(cmd["unitId"], Pos(cmd["targetX"], cmd["targetY"]))
        elif ctype == "Skill":
            target = None
            if cmd.get("targetX", -1) >= 0 and cmd.get("targetY", -1) >= 0:
                target = Pos(cmd["targetX"], cmd["targetY"])
            ok = self.engine.use_skill(cmd["unitId"], cmd["skillId"], target)
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


class BattleTCPHandler(socketserver.StreamRequestHandler):
    host: BattleHost

    def handle(self) -> None:
        self.host.register(self.request)
        try:
            welcome = {"type": "welcome", "seed": self.host.seed, "bossId": self.host.boss_id}
            self._send(welcome)
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
            self._json_response(200, {"ok": True, "bossId": self.battle_host.boss_id})
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Aetherboard authoritative battle host")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8767, help="TCP port (Unity)")
    parser.add_argument("--http-port", type=int, default=8768, help="HTTP port (Web browser)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--boss", default="earth", choices=["earth", "wind"])
    args = parser.parse_args()

    battle_host = BattleHost(seed=args.seed, boss_id=args.boss)

    http_server = BattleHTTPServer((args.host, args.http_port), battle_host)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()

    tcp_server = BattleTCPServer((args.host, args.port), battle_host)
    print(
        f"Aetherboard host: TCP {args.host}:{args.port} | "
        f"HTTP {args.host}:{args.http_port} (boss={args.boss}, seed={args.seed})"
    )
    try:
        tcp_server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down host.")
        tcp_server.shutdown()
        http_server.shutdown()


if __name__ == "__main__":
    main()
