#!/usr/bin/env python3
"""Authoritative battle host — newline-delimited JSON over TCP.

Clients send command envelopes; host broadcasts state envelopes to all peers.

Usage:
    cd aetherboard
    PYTHONPATH=. python3 scripts/battle_host.py --port 8767
"""

from __future__ import annotations

import argparse
import json
import socket
import socketserver
import threading
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

    def export_state(self) -> dict[str, Any]:
        return state_to_dict(self.engine.state, self.engine.boss_id)

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
            welcome = {
                "type": "welcome",
                "seed": self.host.seed,
                "bossId": self.host.boss_id,
            }
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

                if envelope.get("type") != "command":
                    self._send({"type": "error", "message": "Expected command envelope"})
                    continue

                cmd = envelope.get("cmd", {})
                with self.host.lock:
                    ok, err = self.host.apply_command(cmd)
                    state_msg = {"type": "state", "payload": self.host.export_state()}
                if not ok:
                    self._send({"type": "error", "message": err or "rejected"})
                self.host.broadcast(state_msg)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Aetherboard authoritative battle host")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--boss", default="earth", choices=["earth", "wind"])
    args = parser.parse_args()

    battle_host = BattleHost(seed=args.seed, boss_id=args.boss)
    server = BattleTCPServer((args.host, args.port), battle_host)
    print(f"Aetherboard host listening on {args.host}:{args.port} (boss={args.boss}, seed={args.seed})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down host.")
        server.shutdown()


if __name__ == "__main__":
    main()
