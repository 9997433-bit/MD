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

### 3. 一键生成全部场景（推荐）

菜单栏：**Cosmic Front → Setup All Scenes (Hangar + Battle)**

会创建：
- `Hangar.unity` — 机库选阵营/机甲
- `Map_ColonyRim.unity` — 战斗地图（含 XR Rig、HUD、敌机刷新）
- 自动写入 **Build Settings**

也可单独生成：
- **Cosmic Front → Setup Hangar Scene**
- **Cosmic Front → Setup P1 Prototype Scene**

### 4. 运行流程

1. 打开 `Hangar.unity` → Play → 选阵营/机甲 → **开始任务**
2. 进入战斗地图，击坠敌机
3. 时间结束或按结算界面 **返回机库**

### 5. 编辑器测试键位

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
| P1 单机切片 | ✅ | 核心脚本 + Editor 场景向导 |
| P1.5 VR 输入 | ✅ | VRMechInput、Snap Turn、机库场景、XR Rig |
| P2 多人 LAN | ✅ | Fish-Net Host/Join、NetworkMechSync |
| P3 Dedicated + 记分 | ✅ | 无头 Server、击杀榜同步、小行星地图 |
| P4 可玩战舰 | ✅ | Aegis 护卫舰四席位 + 弹射 |
| P5 模式 + Steam | ✅ | Escort / Domination + Steam 骨架 |
| P6 打磨上架 | ⏳ | 美术、平衡、Steam 正式 API |

## VR 配置

1. **Edit → Project Settings → XR Plug-in Management** → 启用 OpenXR
2. 运行 **Setup All Scenes** 会自动创建 `XROrigin`（含 Camera、PlayerMechBinder、Snap Turn）
3. 戴上头显 Play — 自动切换 VR 输入

详见 [VR 操作说明](docs/VR_CONTROLS.md)

### 可选：替换为 XRI Starter Assets

导入 XR Interaction Toolkit Samples 后，用官方 XR Origin 替换场景中的 `XROrigin` 对象，保留 `PlayerMechBinder` 与 `VRSnapTurn` 组件。

## 游戏模式（P5）

机库可选：**团队死斗 / 护送旗舰 / 据点争夺**。Steam 默认离线骨架，详见 [GAME_MODES.md](docs/GAME_MODES.md)。

## 战舰（P4）

机库「生成方式」可选舵手/炮手/舰长；战斗中按 **B** 登舰、**X** 离舰、**L** 弹射。详见 [SHIP_SYSTEM.md](docs/SHIP_SYSTEM.md)。

## Dedicated Server（P3）

菜单 **Cosmic Front → Build → Dedicated Server**，运行：

```bash
CosmicFrontServer.exe -batchmode -nographics -cosmicServer
```

客户端 Join 填服务器 IP。详见 [DEDICATED_SERVER.md](docs/DEDICATED_SERVER.md)。

## 多人联机（P2）

1. 运行 **Setup All Scenes** 生成 NetworkManager
2. `Hangar.unity` → **Host 局域网** 或 **Join 局域网**
3. 详见 [MULTIPLAYER_SETUP.md](docs/MULTIPLAYER_SETUP.md)

## 文档

- [Project Brief](docs/PROJECT_BRIEF.md)
- [GDD](docs/GDD.md)
- [原创 IP 圣经](docs/IP_BIBLE.md)
- [网络规划](docs/NETWORK_PLAN.md)
- [多人联机指南](docs/MULTIPLAYER_SETUP.md)
- [Dedicated Server](docs/DEDICATED_SERVER.md)
- [战舰系统](docs/SHIP_SYSTEM.md)
- [游戏模式与 Steam](docs/GAME_MODES.md)

## 许可

代码：MIT（见 LICENSE，如未添加则默认项目内学习用途）。  
**不得**使用 GUNDAM 相关美术/名称进行商业发布。
