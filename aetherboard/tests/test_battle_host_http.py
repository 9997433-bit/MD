"""HTTP API tests for battle_host."""

from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request

from scripts.battle_host import BattleHost, BattleHTTPServer


class BattleHostHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.host = BattleHost(seed=42, boss_id="earth")
        cls.http = BattleHTTPServer(("127.0.0.1", 18768), cls.host)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.http.shutdown()

    def _get(self, path: str) -> dict:
        with urllib.request.urlopen(f"http://127.0.0.1:18768{path}") as res:
            return json.loads(res.read().decode())

    def _post(self, path: str, body: dict) -> dict:
        data = json.dumps(body).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:18768{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())

    def test_health_and_state(self) -> None:
        health = self._get("/api/health")
        self.assertTrue(health["ok"])
        state = self._get("/api/state")
        self.assertEqual(state["type"], "state")
        self.assertEqual(state["payload"]["bossId"], "earth")

    def test_move_command(self) -> None:
        cmd = {
            "type": "command",
            "cmd": {
                "type": "Move",
                "unitId": "knight",
                "skillId": "",
                "targetX": 3,
                "targetY": 6,
                "bossId": "",
            },
        }
        res = self._post("/api/command", cmd)
        knight = next(u for u in res["payload"]["party"] if u["id"] == "knight")
        self.assertEqual(knight["pos"], {"x": 3, "y": 6})


if __name__ == "__main__":
    unittest.main()
