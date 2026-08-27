# Cosmic Front VR

原创宇宙战争题材 **VR 多人对战平台**（当前阶段：P1 单机垂直切片）。

> 借鉴太空战争场景与团队对战结构，**不使用** GUNDAM / SEED 任何商标与资产。

## 环境要求

- Unity **2022.3 LTS**（推荐 2022.3.62f1）
- VR 头显（可选，Editor 可用键鼠测试）
- Windows PC（PCVR 目标平台）

## 快速开始

### 1. 用 Unity Hub 打开项目

1. 克隆本仓库
2. Unity Hub → **Open** → 选择 `cosmic-front-vr/` 目录
3. 等待 URP / OpenXR / Input System 包导入完成

### 2. 启用 Input System

首次打开时若提示 *Active Input Handling*，选择 **Input System Package (New)** 并重启 Editor。

### 3. 一键生成 P1 试玩场景

菜单栏：**Cosmic Front → Setup P1 Prototype Scene**

会在 `Assets/_Project/Scenes/Map_ColonyRim.unity` 生成：
- 玩家占位机甲（带驾驶舱锚点）
- 敌机 Prefab + 刷新器
- 平台地图

按 **Play** 即可用键鼠试玩。

### 4. 编辑器测试键位

| 操作 | 按键 |
|------|------|
| 移动 | W/A/S/D |
| 上升/下降 | R / F |
| 机体左右转 | Q / E |
| 俯仰 | T / G |
| 冲刺 | Left Shift |
| 主武器 | 鼠标左键 |
| 副武器 | 鼠标右键 |
| 锁定 | Tab（按住自动锁定最近目标） |

## 项目结构

```
cosmic-front-vr/
├── Assets/_Project/
│   ├── Scripts/
│   │   ├── Core/       # GameManager, Health, Bootstrap
│   │   ├── Mech/       # 移动、输入、机体控制
│   │   ├── Combat/     # 锁定、武器、弹道
│   │   ├── AI/         # 敌机 AI、刷新
│   │   ├── Player/     # VR 绑定、Comfort
│   │   ├── UI/         # HUD、机库、结算
│   │   ├── Network/    # P2 占位
│   │   └── Editor/     # 场景生成向导
│   ├── Scenes/
│   └── Prefabs/
├── docs/               # GDD、IP 圣经、网络规划
└── Packages/manifest.json
```

## 开发阶段

| 阶段 | 状态 | 内容 |
|------|------|------|
| P0 文档 | ✅ | `docs/` |
| P1 单机切片 | 🔄 | 核心脚本 + Editor 场景向导 |
| P2 多人 | ⏳ | 见 `docs/NETWORK_PLAN.md` |
| P3 Steam MVP | ⏳ | 匹配、2 图 2 机 |
| P4 战舰 | ⏳ | 见 GDD |

## VR 配置（下一步）

1. **Edit → Project Settings → XR Plug-in Management** → 启用 OpenXR
2. 场景中添加 **XR Origin (Action-based)**（来自 XR Interaction Toolkit 样例）
3. 将 `PlayerMechBinder` 挂到 XR Origin，绑定玩家机甲 CockpitAnchor
4. 在 `FallbackMechInput` 同级添加基于 Input System 的 VR 输入（P1.5）

## 文档

- [Project Brief](docs/PROJECT_BRIEF.md)
- [GDD](docs/GDD.md)
- [原创 IP 圣经](docs/IP_BIBLE.md)
- [网络规划](docs/NETWORK_PLAN.md)

## 许可

代码：MIT（见 LICENSE，如未添加则默认项目内学习用途）。  
**不得**使用 GUNDAM 相关美术/名称进行商业发布。
