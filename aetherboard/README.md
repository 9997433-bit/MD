# Aetherboard — FF14 风格 VR 互动战棋

从《最终幻想14：重生之境》战斗节奏提炼的 **GCD 战棋原型**：先以 Python 模拟 + 2D Web 验证玩法，再迁移到 Unity/OpenXR VR。

## 快速开始

### 1. 运行 Python 战斗模拟与测试

```bash
cd aetherboard
PYTHONPATH=. python3 -m unittest discover -s tests -q
PYTHONPATH=. python3 scripts/run_sim_demo.py
```

### 2. 启动 2D 可玩原型（浏览器）

```bash
cd aetherboard/web
python3 -m http.server 8765
```

打开 http://localhost:8765

**联机模式**：先启动 Host，再打开 http://localhost:8765/?client=1

## 项目结构

| 路径 | 说明 |
|------|------|
| `sim/` | Python 确定性战斗状态机 |
| `web/` | 2D 浏览器可玩原型 |
| `unity/AetherboardVR/` | **Unity VR 项目**（OpenXR + XRI） |
| `csharp/` | C# 核心单元测试（无需 Unity） |
| `schema/` | 战斗状态 JSON Schema |
| `tests/` | Python 单元测试 |
| `docs/` | GDD、VR 路线、Unity 设置指南 |

## Unity VR 快速开始

**最快路径**：Unity Hub 打开 `unity/AetherboardVR` → 打开 `BattleTable` 场景或按 **Play**（自动创建战棋桌）

桌面快捷键：`C` 双人模式 | `Tab` 切换 P1/P2 | `F5`/`F9` 存读档

```bash
# C# 核心测试（无需 Unity）
cd aetherboard/csharp/Aetherboard.Core.Tests && dotnet test
```

Quest 打包见 `docs/QUEST_BUILD.md` · 实机验收见 `docs/QUEST_VERIFICATION.md`

在线同步见 `docs/NETWORK_SYNC.md` · Netcode 见 `docs/NETCODE.md` · 美术见 `docs/ART_ASSETS.md`

### VR 桌面快捷键

| 键 | 功能 |
|----|------|
| `E` / `A` | 结束阶段 / 自动一步 |
| `1` / `2` | 土灵 / 风灵 Boss |
| `C` / `Tab` | 双人模式 / 切换玩家 |
| `H` / `N` / `B` | Host / Client / 切换传输 |
| `F5` / `F9` | 存档 / 读档 |
| `F6` / `F7` | 导出 / 回放命令日志 |

Quest 端使用桌台右侧 **联机 VR 面板** 配置 Host IP。

## 当前 MVP 内容

- **7×7 棋盘**，四职责小队：铁卫 / 白愈 / 黑炎 / 游弦
- **回合阶段**：预警 → 移动 → GCD → oGCD → 结算
- **两名 Boss**：
  - **土灵守护者**：重击 / 地震 / 缩圈 + 土神之怒
  - **风灵领主**：风刃 / 分散 / 集合 + 旋风
- **战术 AI**：自动躲避机制、打断读条、治疗与分散/集合
- **机制预警高亮**：Web 版棋盘显示危险区域预览

## 操作说明（Web）

1. 点击左侧小队成员选中
2. **移动阶段**：点击可达格子移动
3. **GCD / oGCD 阶段**：点技能按钮，再点目标格（治疗点友方，攻击点 Boss 格）
4. **结束当前阶段** 推进；未操作单位会自动使用默认技能
5. **自动演示一步** 快速观看 AI 对战

## 下一步（VR）

见 `docs/VR_ROADMAP.md`：Unity + OpenXR、桌面战棋桌、手柄抓取棋子与技能环。
