# Unity VR 项目设置指南

## 环境要求

| 组件 | 版本 |
|------|------|
| Unity | 2022.3 LTS 或更高 |
| OpenXR Plugin | 1.12+ |
| XR Interaction Toolkit | 3.0+ |
| URP（可选） | 14.0+ |
| 目标平台 | Meta Quest 2/3、PCVR |

## 打开项目

Unity Hub → Add → 选择 `aetherboard/unity/AetherboardVR`

首次打开会自动解析 `Packages/manifest.json` 中的依赖。

## 一键首次设置（推荐）

```
Aetherboard → First Time Setup (Recommended)
```

将依次完成：

1. Quest Android 构建配置（`com.aetherboard.vr`）
2. URP 管线（若包已解析）
3. Battle Table Styled Prefab 安装
4. XR Origin Prefab 安装
5. 创建 `BattleTable.unity` 场景（若不存在）
6. Quest 预检报告

完成后 **按 Play** 即可在桌面模式验证 7×7 战棋桌。

## 最快验证：直接 Play

1. 打开任意场景（或 `Assets/Aetherboard/Scenes/BattleTable.unity`）
2. **按 Play** — `RuntimeSceneBootstrap` 自动创建战棋桌、棋子、HUD、相机
3. 桌面快捷键见 [`README.md`](../README.md)

### VR 操作（头显 / Quest）

| 输入 | 功能 |
|------|------|
| **抓取棋子**（Grip） | 移动阶段拖拽 → 松手吸附格子 |
| 视线 + 扳机 | 选中棋子 |
| Grip（无抓取时） | 对最近棋子打开技能环 |
| A / Primary | 结束当前阶段 |
| B / Secondary | 自动演示一步 |

Quest 联机：桌台右侧 **BattleNetVRPanel** 配置 Host IP。

## 分步设置（可选）

| 菜单 | 说明 |
|------|------|
| `Configure URP Pipeline` | URP Asset + Volume Profile |
| `Install Battle Table Prefabs` | Resources 桌台/格子/棋子 |
| `Install XR Origin Prefab` | 官方 XRI Rig |
| `Create Battle Scene File` | 保存正式场景 |
| `Configure Quest (Android) Build Settings` | ARM64 / IL2CPP |

美术替换见 [`ART_ASSETS.md`](./ART_ASSETS.md) · Quest 打包见 [`QUEST_BUILD.md`](./QUEST_BUILD.md)

## 项目结构

```
unity/AetherboardVR/
  Assets/Aetherboard/
    Scripts/Core/       # 纯 C# 战斗核心（无 Unity 依赖）
    Scripts/VR/         # 桌台、抓取、VFX、HUD、网络
    Scripts/Netcode/    # NGO 传输
    Scripts/Editor/     # 打包、侧载、美术、首次设置向导
    Resources/Aetherboard/   # Prefab（Editor 菜单安装）
    Scenes/BattleTable.unity
  Packages/manifest.json
```

## 测试

```bash
cd aetherboard
./scripts/run_all_tests.sh          # Python + C# + 脚本语法
./scripts/release_preflight.sh      # 合并前预检
./scripts/quest_verify.sh           # Quest 烟测（需 adb + APK）
```

C# 核心与 Python `sim/` 对齐，共享 `schema/battle_state.schema.json`。

## 联机

| 传输 | 端口 | 说明 |
|------|------|------|
| TCP | 8767 | Python / Unity Host |
| WebSocket | 8769 | Web / Unity Client |
| NGO UnityTransport | 7777 | NetcodeNative |

详见 [`NETCODE.md`](./NETCODE.md) · [`NETWORK_SYNC.md`](./NETWORK_SYNC.md)

## 相关文档

- [`VR_ROADMAP.md`](./VR_ROADMAP.md) — 功能清单
- [`QUEST_VERIFICATION.md`](./QUEST_VERIFICATION.md) — Quest 实机验收
- [`PR_MERGE.md`](./PR_MERGE.md) — PR 合并指南
