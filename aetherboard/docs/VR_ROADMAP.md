# VR 迁移路线

## 当前进度

| 步骤 | 状态 | 产物 |
|------|------|------|
| Python 战斗模拟 | ✅ | `sim/` |
| 2D Web 可玩原型 | ✅ | `web/` |
| JSON Schema | ✅ | `schema/battle_state.schema.json` |
| C# 战斗核心移植 | ✅ | `unity/.../Scripts/Core/` |
| C# 单元测试 | ✅ | `csharp/Aetherboard.Core.Tests/` |
| VR 交互脚本 | ✅ | `unity/.../Scripts/VR/` |
| Unity 场景 / Prefab | 🔲 | 需在 Editor 中完成（见 UNITY_SETUP.md） |
| 机制 VFX 美术 | 🔲 | Telegraph 圈 / 读条条 |
| 在线多人 | 🔲 | Host 权威同步 |

## 技术栈

- **引擎**：Unity 2022 LTS+
- **XR**：OpenXR（Meta Quest + PCVR）
- **交互**：XR Interaction Toolkit 3.0（抓取 + Snap Grid）
- **网络（后期）**：Host 权威回合状态同步

## 架构

```
VR Client (Unity)
  ├── BattleDirector     # 战斗编排入口
  ├── BattleTableView    # 7×7 桌台 + 棋子
  ├── PieceToken         # XR Grab → 格子吸附
  ├── SkillRingController# GCD / oGCD 技能环
  ├── TelegraphVFXController # 预警圈 + 读条
  └── BossHologramView   # Boss 全息 UI

Battle Sim (C# Core)
  └── 与 Python sim/ 规则对齐，JSON Schema 同步
```

## 快速开始

```bash
# C# 核心测试（无需 Unity）
cd aetherboard/csharp/Aetherboard.Core.Tests && dotnet test

# Unity 项目
# Unity Hub → 打开 aetherboard/unity/AetherboardVR
# 菜单 Aetherboard → Create Battle Root
```

完整步骤见 [UNITY_SETUP.md](./UNITY_SETUP.md)。

## 首版 VR 范围

- 单人 vs 土灵守护者 / 风灵领主
- 1 张桌台场景
- 抓取棋子 + 技能环 + 预警高亮
- 坐姿 / 站姿桌台高度

## 参考

- *Demeo* — VR 桌游交互
- *Tabletop Simulator VR* — 抓取与摆放
- FF14 ARR 极神 — 机制可读性
