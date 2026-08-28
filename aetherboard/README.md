# Aetherboard — FF14 风格 VR 互动战棋

从《最终幻想14：重生之境》战斗节奏提炼的 **GCD 战棋**：Python 模拟 → 2D Web 原型 → **Unity VR 可玩版本**（OpenXR / Meta Quest）。

## 里程碑状态

| 模块 | 状态 |
|------|------|
| Python 战斗核心 + 测试 | ✅ 22 tests |
| 2D Web 可玩原型 | ✅ |
| C# 战斗核心 + 测试 | ✅ 14 tests |
| Unity VR 交互 / VFX / 音效 | ✅ |
| 三路联机（TCP / WS / NGO） | ✅ |
| Quest 打包 / 侧载 / 验收工具链 | ✅ |
| **四 Boss（土/风/冰/火）** | ✅ v0.4.0-vr |
| Quest 实机 11 项人工验收 | 🔲 见 `docs/QUEST_VERIFICATION.md` |

完整功能清单见 [`docs/VR_ROADMAP.md`](docs/VR_ROADMAP.md)。

## 快速开始

### Python + Web（无需 Unity）

```bash
cd aetherboard
PYTHONPATH=. python3 -m unittest discover -s tests -q
PYTHONPATH=. python3 scripts/run_sim_demo.py

cd web && python3 -m http.server 8765
# 打开 http://localhost:8765
# 联机：先 python3 scripts/battle_host.py --coop，再 ?client=1
```

### C# 核心测试（无需 Unity）

```bash
cd aetherboard && ./scripts/run_all_tests.sh       # 本地 CI
cd aetherboard && ./scripts/release_preflight.sh   # 合并前预检
```

### Unity VR

1. Unity Hub 打开 `unity/AetherboardVR`
2. 菜单：`Aetherboard → First Time Setup (Recommended)`（一键配置）
3. **Play**（自动创建 7×7 战棋桌）

分步配置：`Configure URP Pipeline` → `Install Battle Table Prefabs` → `Install XR Origin Prefab`

Quest 打包与实机验收见 [`docs/QUEST_BUILD.md`](docs/QUEST_BUILD.md) · [`docs/QUEST_VERIFICATION.md`](docs/QUEST_VERIFICATION.md)

**Quest 一键烟测（需 adb + 已构建 APK）：**

```bash
cd aetherboard
./scripts/quest_verify.sh
```

## 项目结构

| 路径 | 说明 |
|------|------|
| `sim/` | Python 确定性战斗状态机 |
| `web/` | 2D 浏览器可玩原型 + 读条 UI |
| `unity/AetherboardVR/` | Unity VR 项目（OpenXR + XRI + NGO） |
| `csharp/` | C# 核心单元测试 |
| `schema/` | 战斗状态 JSON Schema |
| `scripts/` | Host 服务、Quest 烟测脚本 |
| `docs/` | GDD、VR 路线、联机、Quest、美术指南 |

## VR 功能概览

- **7×7 桌台**：抓取棋子、格子吸附、技能环 VR 射线
- **四 Boss**：土灵 / 风灵 / 冰灵 / 火灵，读条 VFX + 机制预警
- **双人协作**：P1 铁卫/游弦，P2 白愈/黑炎
- **联机**：Host 权威，TCP `8767` / WS `8769` / NGO `7777`
- **美术**：Styled Prefab + FBX 导入向导 + URP 后处理
- **Quest 工具**：APK 构建、ADB 侧载、验收报告导出

## 桌面 / VR 快捷键

| 键 | 功能 |
|----|------|
| `E` / `A` | 结束阶段 / 自动一步 |
| `1` / `2` / `3` / `4` | 土灵 / 风灵 / 冰灵 / 火灵 Boss |
| `C` / `Tab` | 双人模式 / 切换玩家 |
| `H` / `N` / `B` | Host / Client / 切换传输 |
| `F5` / `F9` | 存档 / 读档 |
| `F6` / `F7` | 导出 / 回放命令日志 |

Quest 端使用桌台右侧 **联机 VR 面板** 配置 Host IP。

## MVP 机制

| Boss | 阶段机制 |
|------|----------|
| 土灵守护者 | 重击 → 地震 → 缩圈 + 土神之怒（可打断读条） |
| 风灵领主 | 风刃 → 分散 → 集合 + 旋风 |

四职责小队：铁卫 / 白愈 / 黑炎 / 游弦。回合流：预警 → 移动 → GCD → oGCD → 结算。

## 文档索引

| 文档 | 内容 |
|------|------|
| [VR_ROADMAP.md](docs/VR_ROADMAP.md) | 功能清单与架构 |
| [NETCODE.md](docs/NETCODE.md) | NGO / 联机架构 |
| [NETWORK_SYNC.md](docs/NETWORK_SYNC.md) | Host 权威同步 |
| [QUEST_BUILD.md](docs/QUEST_BUILD.md) | Quest APK 打包 |
| [QUEST_VERIFICATION.md](docs/QUEST_VERIFICATION.md) | 实机验收清单 |
| [ART_ASSETS.md](docs/ART_ASSETS.md) | 美术替换与 FBX 导入 |
| [URP_SETUP.md](docs/URP_SETUP.md) | URP 渲染管线 |
| [PR_MERGE.md](docs/PR_MERGE.md) | PR 合并指南 |
| [GITHUB_PR_BODY.md](docs/GITHUB_PR_BODY.md) | PR #5 描述模板 |
| [CHANGELOG.md](CHANGELOG.md) | 版本记录 |

## CI

GitHub Actions：`.github/workflows/aetherboard-tests.yml`（Python + C#）
