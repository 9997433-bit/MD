# Meta Quest 实机验证指南

本指南用于侧载 APK 并在 Quest 头显上验证 Aetherboard VR 战斗桌功能。

## 前置条件

- Quest 2 / Quest 3 开启**开发者模式**（Meta Quest 手机 App → 设备 → 开发者模式）
- USB 连接 PC，或启用**无线 ADB**
- Unity 项目已配置 Android SDK（`ANDROID_HOME` 或 Unity Hub → Android Build Support）
- PC 与 Quest 在同一局域网（联机测试）

## 一键流程（Editor）

```
1. Aetherboard → Configure Quest (Android) Build Settings   （首次）
2. Aetherboard → Install Battle Table Prefabs               （可选，推荐）
3. Aetherboard → Install XR Origin Prefab                     （可选，推荐）
4. Aetherboard → Build Quest APK to build/                  （输出 build/AetherboardVR.apk）
5. Aetherboard → Quest → Check Connected Device (ADB)       （确认设备在线）
6. Aetherboard → Quest → Install Last Built APK             （侧载）
```

Quest 头显：**资料库 → 未知来源** → 启动 **Aetherboard VR**。

## 运行时诊断

Quest 启动后，`QuestRuntimeDiagnostics` 自动在 logcat 输出：

- 设备型号 / GPU
- XR 是否启用
- 桌台来源（Prefab / Procedural）
- **LAN IP**（联机时填入 PC Host 地址）
- **自动验收检查**（PASS/FAIL）：BattleDirector、棋子数量、XR 等

```bash
# 查看 Android 日志
adb logcat -s Unity | grep Aetherboard
```

## 功能验证清单

| # | 测试项 | 操作 | 预期 |
|---|--------|------|------|
| 1 | 启动 | 打开应用 | 看到 7×7 战棋桌，无黑屏 |
| 2 | 帧率 | 正常环视 | 稳定 72fps（Quest 2） |
| 3 | 抓取 | 手柄抓取棋子 | 棋子跟随手柄，松手吸附格子 |
| 4 | 移动 | 抓取放到合法格 | Host 权威下棋子落位，阶段推进 |
| 5 | 技能环 | 扳机打开技能环 | 芯片高亮，可选技能 |
| 6 | 读条 VFX | Boss 读条时 | 进度环 + 紧急脉冲可见 |
| 7 | 双人 | `C` 切换双人（桌面）/ HUD | P1/P2 权限正确 |
| 8 | 联机 WS | PC Host `H`，Quest Client `N` + WS | 状态同步 |
| 9 | 联机 NGO | PC Host `H`，Quest `N` + **NetcodeNative** | 端口 7777 同步 |
| 10 | 音效 | 阶段切换 / 伤害 | 程序化音效播放 |

## 联机配置（Quest → PC Host）

### PC 端

```bash
# 方式 A：Python Host（Web / WS 客户端）
cd aetherboard && PYTHONPATH=. python3 scripts/battle_host.py --coop

# 方式 B：Unity Host
Play → H（TCP 8767 + WS 8769 + NGO 7777）
```

记录 PC 局域网 IP（如 `192.168.1.42`）。

### Quest 端

1. 启动 Aetherboard VR
2. 看向桌台右侧 **联机面板**（或左上角 IMGUI HUD）
3. 点击 **键盘输入** 输入 PC 局域网 IP（如 `192.168.1.42`），或桌面模式直接编辑 Host IP 字段
4. 点击 **Client** 连接
5. 若失败，点 **传输切换** 尝试 WebSocket / NetcodeNative

> 设置会自动保存到 PlayerPrefs，下次启动无需重输。

> Player Settings 已启用 **Internet Access**（`forceInternetPermission`）。

## 常见问题

| 问题 | 解决 |
|------|------|
| adb devices 为空 | 换 USB 线、授权调试弹窗、重装驱动 |
| 黑屏 | 确认 OpenXR Loader 已启用；先用桌面 Play 验证逻辑 |
| 无法抓取 | 需 XR Origin + Ray/Grab Interactor；运行 Install XR Origin Prefab |
| 联机失败 | 检查防火墙、同一 Wi-Fi、IP 是否正确 |
| APK 安装失败 | `adb uninstall com.aetherboard.vr` 后重装 |

## 相关文档

- [QUEST_BUILD.md](./QUEST_BUILD.md) — 打包配置
- [NETCODE.md](./NETCODE.md) — NGO 传输说明
