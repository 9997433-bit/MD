# Unity VR 项目设置指南

## 环境要求

| 组件 | 版本 |
|------|------|
| Unity | 2022.3 LTS 或更高 |
| OpenXR Plugin | 1.12+ |
| XR Interaction Toolkit | 3.0+ |
| 目标平台 | Meta Quest 3 / Quest 2、PCVR（SteamVR / Link） |

## 打开项目

```bash
# Unity Hub → Add → 选择目录
aetherboard/unity/AetherboardVR
```

首次打开会自动解析 `Packages/manifest.json` 中的 OpenXR 与 XRI 依赖。

## 最快验证：直接 Play

1. 打开任意空场景（默认场景即可）
2. **按 Play** — 系统自动创建战棋桌、棋子、HUD、相机
3. 桌面操作：
   - 点击棋子 → 点击格子移动
   - `E` 结束阶段 | `A` 自动一步
   - `1` 土灵 Boss | `2` 风灵 Boss
   - `C` 切换双人模式 | `Tab` 切换 P1/P2
   - **右键** 打开技能环（GCD/oGCD 阶段）→ 点击技能芯片 → 点击目标格

### VR 操作（头显模式）

| 输入 | 功能 |
|------|------|
| **抓取棋子**（Grip） | 移动阶段拖拽 → 松手吸附到最近格子 |
| 视线 + 扳机 | 选中棋子（桌面/射线模式） |
| Grip（无抓取时） | 对最近棋子打开技能环 |
| A / Primary | 结束当前阶段 |
| B / Secondary | 自动演示一步 |

抓取移动时，目标格子会高亮显示；非法移动会弹回原位。双人模式下仅可抓取己方棋子。

也可通过菜单 `Aetherboard → Create Battle Scene File` 保存正式场景。

### 官方 XR Origin 预制体（推荐）

1. 菜单 **Aetherboard → Install XR Origin Prefab**（从 XRI 包复制官方 Rig）
2. 预制体保存至 `Assets/Aetherboard/Resources/Aetherboard/XROriginRig.prefab`
3. 运行时 `XRRigFactory` 优先加载该预制体（`RuntimeSceneBootstrap.rigSource = Auto`）
4. 若未安装，自动回退到程序化 XR Rig 或桌面相机

## VR 场景搭建（Quest / PCVR）

1. `GameObject > XR > XR Origin (VR)` 创建玩家 Rig
2. `Project Settings > XR Plug-in Management` 勾选 **OpenXR**
3. OpenXR 特性中启用 **Meta Quest Support**（Quest）或 **Oculus Touch Controller Profile**（PCVR）

### 2. 战棋桌

创建空物体 `BattleRoot`，挂载：

| 组件 | 说明 |
|------|------|
| `BattleDirector` | 战斗状态机入口 |
| `BattleTableView` | 7×7 格子渲染 |
| `TelegraphVFXController` | 机制预警圈 |
| `BossHologramView` | Boss 全息 UI |
| `VRBattleBootstrap` | 自动连线 |

### 3. 预制体（Prefabs）

在 `Assets/Aetherboard/Prefabs/` 创建：

- **GridCell** — 薄立方体 + `GridCell` 脚本 + MeshRenderer
- **PieceToken** — 胶囊体 + `XRGrabInteractable` + `PieceToken`
- **PreviewRing** — 扁圆环，用于预警高亮
- **SkillRingButton** — 世界空间 Canvas 按钮

将 Prefab 拖入 `BattleTableView` 的序列化字段。

### 4. 交互流程

```
预警阶段 → 棋盘显示橙色预警圈
移动阶段 → 抓取棋子 → 松手吸附到格子
GCD 阶段 → 指向棋子 → 技能环展开 → 选择技能
oGCD 阶段 → 手腕快捷栏 / 技能环
结算阶段 → VFX 播放 → 自动进入下一回合
```

### 5. 坐姿模式

`VRBattleBootstrap.seatedMode = true` 将桌台固定在腰部高度（默认 0.75m）。

## C# 核心测试（无需 Unity）

```bash
cd aetherboard/csharp/Aetherboard.Core.Tests
dotnet test
```

战斗逻辑与 Python `sim/` 对齐，共享 `schema/battle_state.schema.json`。

## 目录结构

```
unity/AetherboardVR/
  Assets/Aetherboard/
    Scripts/Core/     # 纯 C# 战斗模拟（无 Unity 依赖）
    Scripts/VR/       # 桌台、抓取、技能环、VFX
    Prefabs/          # 需自行创建（见上）
  Packages/manifest.json
```

## 下一步开发

- [ ] 完成 Prefab 与 `BattleTable.unity` 场景
- [ ] 机制 VFX：缩圈光墙、地震裂纹材质
- [ ] 读条条 Animancer / Timeline
- [ ] 本地双人：第二套 XR Origin 或非对称 PC 协控
- [ ] 网络：Host 权威 + `battle_state.schema.json` 同步
