# PR 合并指南 — Aetherboard VR Milestone

分支：`cursor/vr-battle-board-e6ea` → `main`

## 变更范围

本里程碑将 Aetherboard 从 Python/Web 原型完整迁移至 **Unity VR 可玩版本**，涵盖战斗核心、XR 交互、三路联机、Quest 工具链与美术体系。

## 核心模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 战斗核心 | `unity/.../Core/` | C# 引擎，对齐 `sim/` |
| VR 层 | `unity/.../VR/` | 交互、VFX、HUD、网络 |
| NGO | `unity/.../Netcode/` | CustomMessaging + UnityTransport |
| Web | `web/` | 2D 原型 + 读条 UI |
| Host | `scripts/battle_host.py` | Python 权威服务器 |

## 测试

```bash
# Python 19 tests
cd aetherboard && PYTHONPATH=. python3 -m unittest discover -s tests -q

# C# 13 tests
cd aetherboard/csharp/Aetherboard.Core.Tests && dotnet test
```

CI：`.github/workflows/aetherboard-tests.yml`

## Unity 首次打开清单

1. `Aetherboard → Configure URP Pipeline`
2. `Aetherboard → Install Battle Table Prefabs`
3. `Aetherboard → Install XR Origin Prefab`
4. Play 验证桌面模式
5. `Build Quest APK to build/` + `Quest → Install Last Built APK`
6. `Quest → Run Pre-Build Readiness Check` 或 `./scripts/quest_verify.sh`

## 文档索引

- [VR_ROADMAP.md](./VR_ROADMAP.md) — 功能清单
- [CHANGELOG.md](../CHANGELOG.md) — 版本记录
- [NETCODE.md](./NETCODE.md) — 联机架构
- [QUEST_VERIFICATION.md](./QUEST_VERIFICATION.md) — 实机验收
- [ART_ASSETS.md](./ART_ASSETS.md) — 美术替换
- [URP_SETUP.md](./URP_SETUP.md) — 渲染管线

## 合并后待办（人工）

- [ ] Quest 头显实机验收（10 项清单）
- [x] FBX 导入向导（`Aetherboard → Art` 菜单）
- [ ] 可选：替换 `Resources/Aetherboard/Art/Models/` 正式 FBX
- [x] URP 后处理 Volume（Bloom / 色彩 / 暗角）

## 破坏性变更

无。Python/Web Host 协议保持兼容（TCP 8767 / WS 8769）。
