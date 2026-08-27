# Meta Quest 打包指南

## 前置条件

- Unity 2022.3 LTS+
- Android Build Support（SDK、NDK、OpenJDK）
- Meta Quest 开发者账号（侧载测试）

## 一键配置（Editor）

```
菜单 Aetherboard → Configure Quest (Android) Build Settings
```

将自动设置：

- 平台 Android
- IL2CPP + ARM64
- Linear 色彩空间

## OpenXR 配置步骤

1. **XR Plug-in Management**
   - `Edit → Project Settings → XR Plug-in Management`
   - Android 标签页勾选 **OpenXR**

2. **OpenXR 特性**
   - `Project Settings → OpenXR`
   - 添加 Interaction Profile：
     - `Oculus Touch Controller Profile`（Quest 2/3）
     - `Meta Quest Touch Plus Controller Profile`（Quest 3）

3. **XR Interaction Toolkit**
   - 已包含在 `Packages/manifest.json`
   - 场景中可替换 `RuntimeSceneBootstrap` 自动相机为：
     - `GameObject → XR → XR Origin (VR)`

4. **Quest 特定设置**
   - `Project Settings → Player → Android`
   - Minimum API Level: **29+**
   - Target API Level: 自动或 32+
   - 勾选 **Internet Access**（若后续加网络）

## 构建 APK

1. `File → Build Settings`
2. 确认场景 `Assets/Aetherboard/Scenes/BattleTable.unity` 在列表中  
   （或任意空场景 + Runtime 自动加载）
3. `Build And Run`（Quest 通过 USB 连接并开启开发者模式）

## 桌面快速验证（无需头显）

1. 打开项目，直接 **Play**
2. `RuntimeSceneBootstrap` 自动生成战棋桌
3. 操作：
   - 点击棋子 → 点击格子移动
   - `E` 结束阶段 | `A` 自动一步
   - `1` 土灵 Boss | `2` 风灵 Boss
   - `C` 双人模式 | `Tab` 切换玩家
   - `F5` 存档检查点 | `F9` 读档
   - `H` Host | `N` Client | `B` 切换传输层（Auto/WS/TCP）

## 联机（Quest → PC Host）

1. PC 运行 Python Host：`PYTHONPATH=. python3 scripts/battle_host.py --coop`
2. 确认 PC 与 Quest 在同一局域网
3. Unity Client 模式，将 `hostAddress` 设为 PC 局域网 IP
4. 传输层选 **Auto** 或 **WebSocket**（`ws://PC_IP:8769`）
5. Android 需勾选 **Internet Access**（Player Settings）

## 性能建议（Quest）

| 项目 | 建议值 |
|------|--------|
| 渲染 | URP，单方向光 |
| 棋盘 | 程序化几何体（当前默认） |
| 目标帧率 | 72fps（Quest 2）/ 90fps（Quest 3） |
| 桌台面数 | < 5000 tris（当前远低于此） |

## 常见问题

**黑屏**：确认 OpenXR Loader 已启用，或先用桌面模式验证逻辑。

**无法抓取棋子**：场景中需有 XR Origin + XR Ray Interactor；桌面模式用鼠标点击。

**IL2CPP 编译失败**：安装 Android NDK（Unity Hub → Android Build Support）。
