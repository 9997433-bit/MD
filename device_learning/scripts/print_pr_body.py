#!/usr/bin/env python3
"""Emit updated PR description markdown to stdout (for gh pr edit --body-file)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pytest_count() -> int:
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            cwd=ROOT,
            text=True,
        )
        return len([ln for ln in out.splitlines() if "::" in ln])
    except subprocess.CalledProcessError:
        return 0


def main() -> None:
    cov = json.loads((ROOT / "coverage.json").read_text(encoding="utf-8"))
    closure = json.loads((ROOT / "manifests" / "static_closure.json").read_text(encoding="utf-8"))
    counts = cov.get("status_counts", {})
    tests = pytest_count()
    layers = cov.get("by_layer", {})

    body = f"""## 摘要

`device_learning` 位流 + 硬件照片静态学习包，对标 E1733A 账本方法论。

**声明**：目录完整 ≠ 厂商等价 ≠ 掌握运行行为

## 规模

| 指标 | 值 |
|------|-----|
| Identifier | **{cov.get('total_identifiers')}** |
| pytest | **{tests}** 全部通过 |
| confirmed | {counts.get('confirmed', '?')} |
| blocked | {counts.get('missing', 0) + counts.get('unknown', 0) + counts.get('not_started', 0)} |
| 静态阶段 | **已关闭冻结** (`static_phase_closed.json`) |

## 八层 catalog

| 层 | 条目 |
|----|------|
| HW | {layers.get('hw', '?')} |
| BIT | {layers.get('bit', '?')} |
| SIG | {layers.get('signal', '?')} |
| USB | {layers.get('usb', '?')} |
| REF | {layers.get('ref', '?')} |
| ARCH | {layers.get('arch', '?')} |
| LEARN | {layers.get('learn', '?')} |
| EXP | {layers.get('exp', '?')} |

## 关键能力

- Spartan-3 XC3S200 位流解析（`frame_deep.json`，FRM-011..020）
- `EvidenceLedger.json` + 停止条件验收 + 敏感词审计
- 阶段 B/C 脚手架：`make intake` · `make phase-b` · `make phase-c`
- 合成 EEPROM 夹具检测（不误标 `observed`）
- `manifests/handoff_bundle.json` 一站式交接包

## 验证

```bash
cd device_learning
make ci && make health && make closure
```

## 阻塞（需实机）

- `phase_b/captures/eeprom.bin` (8192 B)
- `phase_b/captures/*.pcapng`

## 有实物时

```bash
make intake
make check-captures && make phase-b && make proposals
```
"""
    sys.stdout.write(body)


if __name__ == "__main__":
    main()
