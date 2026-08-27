#!/usr/bin/env python3
"""Run an auto-play demo in the terminal."""

from sim.battle import BattleEngine
from sim.types import Phase


def main() -> None:
    engine = BattleEngine(seed=42)
    engine.begin_warning()
    print("=== Aetherboard 自动演示 ===")
    print(f"Boss: {engine.state.boss.name} HP {engine.state.boss.hp}")
    for _ in range(40):
        if engine.state.phase in {Phase.VICTORY, Phase.DEFEAT}:
            break
        engine.step_auto()
        print(f"\n-- 回合 {engine.state.turn - 1} 结束 | 阶段 {engine.state.boss.phase} --")
        print(f"Boss HP: {engine.state.boss.hp}/{engine.state.boss.max_hp}")
        for unit in engine.state.party:
            status = "存活" if unit.alive else "倒下"
            print(f"  {unit.name}: {unit.hp}/{unit.max_hp} ({status})")
        for entry in engine.state.log.entries[-4:]:
            print(f"  > {entry}")
    print(f"\n结果: {engine.state.phase.name}")


if __name__ == "__main__":
    main()
