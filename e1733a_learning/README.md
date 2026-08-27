# E1733A Static Analysis Learning Package

Keysight E1733A v1.14.1 frozen static analysis ledger for 采集 / 分析 / 补偿.

## Generate

```bash
python3 scripts/generate_ledger.py
pytest tests/ -q
```

## Source

- Installer: `Montyzhang/-seed` → `Install Keysight E1733A 1.14.1 (Win64).exe`
- Extracted payload: 53 files (see `manifests/manifest_files.json`)

## Outputs

| File | Purpose |
|------|---------|
| `EvidenceLedger.json` | Full identifier catalog |
| `coverage.json` | Status counts + stop condition |
| `bridge_matrix.json` | Forced null bridges |
| `manifests/*.json` | File hashes, PE exports, Remote.h constants, samples |

## Stop condition

目录完整 ≠ 厂商软件等价。`ProcessRawData` / ambient body / interpolate 保持 `unknown`。
