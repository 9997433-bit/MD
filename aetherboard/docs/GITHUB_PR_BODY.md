# GitHub PR #5 描述模板

将以下内容复制到 [PR #5](https://github.com/9997433-bit/MD/pull/5) 的 Description，并将标题改为推荐标题。

## 推荐标题

```
feat(aetherboard): VR battle board milestone — Unity OpenXR, netcode, Quest toolchain (v0.2.0-vr)
```

## 推荐描述（复制以下全文）

## 摘要

Aetherboard 从 Python/Web 原型完整迁移至 **Unity VR 可玩版本**（`0.2.0-vr`），涵盖战斗核心、XR 交互、三路联机、Quest 工具链与美术体系。

## 核心模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 战斗核心 | `aetherboard/unity/.../Core/` | C# 引擎，对齐 `sim/` |
| VR 层 | `aetherboard/unity/.../VR/` | 抓取、技能环、VFX、HUD、结算 |
| NGO | `aetherboard/unity/.../Netcode/` | CustomMessaging + UnityTransport 7777 |
| Web | `aetherboard/web/` | 2D 原型 + 读条 UI |
| Host | `aetherboard/scripts/battle_host.py` | Python 权威服务器 |

## 测试

```bash
cd aetherboard && ./scripts/release_preflight.sh
```

- Python: **19/19** ✅
- C#: **13/13** ✅
- CI: `.github/workflows/aetherboard-tests.yml`

## Unity / Quest 快速开始

1. `Aetherboard → First Time Setup (Recommended)`
2. Play 验证桌面模式
3. `Build Quest APK to build/` → `./scripts/quest_verify.sh`

## 文档

- [`aetherboard/README.md`](../README.md)
- [`docs/VR_ROADMAP.md`](./VR_ROADMAP.md)
- [`docs/QUEST_VERIFICATION.md`](./QUEST_VERIFICATION.md)
- [`docs/PR_MERGE.md`](./PR_MERGE.md)

## 合并后人工待办

- [ ] Quest 头显实机 10 项验收（工具链已就绪）
- [ ] 可选：替换正式 FBX 美术资源

## 破坏性变更

无。Python/Web Host 协议保持兼容（TCP 8767 / WS 8769）。
