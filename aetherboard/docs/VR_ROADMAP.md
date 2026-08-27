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
| **运行时自动场景** | ✅ | `RuntimeSceneBootstrap` — 按 Play 即可 |
| **桌面键鼠测试** | ✅ | `DesktopBattleInput` + IMGUI HUD |
| **XR Rig 自动创建** | ✅ | `XRRigFactory`（XRI 可用时） |
| **技能环 UI** | ✅ | `SkillRingController` 世界空间芯片 |
| **读条 / 机制 VFX** | ✅ | `FuryCastBarVFX` + 缩圈脉冲 / 重击震波 |
| Quest 打包向导 | ✅ | Editor 菜单 + `QUEST_BUILD.md` |
| **本地双人协作** | ✅ | `CoopController` — P1 铁卫/游弦，P2 白愈/黑炎 |
| **程序化音效** | ✅ | `BattleAudioController` — 阶段/伤害/读条提示音 |
| **机制粒子 VFX** | ✅ | `BattleParticleVFX` — 预警格粒子爆发 |
| **BattleTable 场景** | ✅ | `Scenes/BattleTable.unity` + `BattleSceneBuilder` |
| **状态 JSON 编解码** | ✅ | `BattleStateCodec` — 对齐 Schema，支持存档/同步 |
| **命令日志** | ✅ | `BattleCommandLog` — 回放与 Host 同步基础 |
| **本地网络桩** | ✅ | `BattleNetSession` — JSON 快照交换 |
| **Host 权威同步** | ✅ | `BattleHostAuthority` + `scripts/battle_host.py` |
| **命令回放** | ✅ | `BattleReplayer` + `BattleCommandExecutor` |
| **TCP 客户端** | ✅ | Unity Client 模式 → Python Host |
| **Unity TCP Host** | ✅ | `BattleTcpHostServer` — 内置 8767 服务 |
| **Web HTTP 客户端** | ✅ | `?client=1` + `hostClient.js` |
| **WebSocket 客户端** | ✅ | `hostWsClient.js` + Unity `BattleWebSocketClient` |
| **双人权限校验** | ✅ | `--coop` + `CoopRules` + `playerId` |
| **命令回放 UI** | ✅ | F6/F7 导出回放 · Web JSON 导入/导出 |
| **Unity WS 传输** | ✅ | Auto WS→TCP 回退，`B` 切换 |
| **XR Origin 官方 Prefab** | ✅ | 菜单安装 + Resources 自动加载 |
| **Unity WS Host** | ✅ | `BattleWebSocketHostServer` 8769 |
| **XR 抓取吸附** | ✅ | `PieceXRGrabController` + 格子高亮 |
| **技能环 VR 射线** | ✅ | 悬停高亮 + 扳机选择 + 不可用灰显 |
| **机制 VFX 升级** | ✅ | 缩圈光墙 / 重击双波 / 风刃 / 集合信标 |
| **读条打断 VFX** | ✅ | 轨道环 + 紧急脉冲 + 打断爆发 |
| **网络传输抽象** | ✅ | `IBattleNetTransport` TCP/WS 可插拔 |
| **Netcode 适配原型** | ✅ | `BattleNetcodeService` + Relay 传输 |
| **Web 读条 UI** | ✅ | 进度条 + 紧急脉冲 + 打断爆发 |
| **NGO CustomMessaging** | ✅ | `BattleNetcodeFacade` + HostCoordinator |
| **Quest APK 构建菜单** | ✅ | `QuestApkBuilder` Editor 菜单 |
| **NGO UnityTransport** | ✅ | `BattleNetcodeNativeTransport` 端口 7777 |
| 在线多人传输层 | ✅ | TCP / WS / NGO 三路并行 |
| Quest 实机验证 | 🔲 | 侧载 APK 联机测试 |

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
# 菜单 Aetherboard → Create Battle Scene File
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
