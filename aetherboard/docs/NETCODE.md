# Unity Netcode 集成指南

Aetherboard 战斗同步已抽象为 `IBattleNetTransport`，并完成 Unity Netcode for GameObjects（NGO）Custom Messaging 实装。

## 当前架构

```
BattleNetSession
  └── IBattleNetTransport
        ├── BattleTcpNetTransport        (8767)
        ├── BattleWebSocketNetTransport  (8769)
        └── BattleNetcodeRelayTransport  (NGO 就绪中继 → WS)
              └── BattleNetcodeService   (本地消息总线)

NGO 层（com.unity.netcode.gameobjects 安装后）
  ├── BattleNetcodeFacade          CustomMessaging 编解码
  ├── BattleNetcodeHostCoordinator NetworkBehaviour 桥接
  └── BattleNetcodeNGOSetup        自动挂载 Coordinator
```

| 组件 | 作用 |
|------|------|
| `BattleNetMessageCodec` | 4 字节长度头 + UTF-8 JSON，兼容 NGO Custom Messaging |
| `BattleNetcodeRuntime` | 运行时检测 `Unity.Netcode` 程序集 |
| `BattleNetcodeService` | VR 层发布/订阅战斗 JSON |
| `BattleNetcodeFacade` | NGO `SendNamedMessageToAll` / 接收回调 |
| `BattleNetcodeHostCoordinator` | Host 广播 + Client 接收，挂于 `NetworkManager` |
| `BattleNetcodeRelayTransport` | 客户端传输：当前走 WS，同时广播到 Service |

## 客户端传输模式

Unity HUD / `B` 键循环：

`Auto` → `WebSocket` → `TCP` → `NetcodeRelay` → `Auto`

**NetcodeRelay** 模式会创建 `BattleNetcodeService`，在 NGO 未安装时自动回退 WebSocket，与 Python Host 完全兼容。

## 安装 Unity Netcode

`Packages/manifest.json` 已包含：

```json
"com.unity.netcode.gameobjects": "1.8.1",
"com.unity.transport": "2.3.0"
```

Editor 菜单：

- `Aetherboard → Netcode → Verify NGO Packages` — 检查 manifest
- `Aetherboard → Netcode → Open Netcode Integration Guide` — 本文档

### Host 场景配置

1. 添加 `NetworkManager` + `UnityTransport`
2. Play → **Start Host**（或 Start Server + Client）
3. `BattleNetcodeNGOSetup` 自动为 `NetworkManager` 添加 `BattleNetcodeHostCoordinator`
4. Unity `H` Host 模式时，`BattleNetSession.PublishHostState` 同时经 TCP/WS/NGO 广播

### 消息格式

发送端：`BattleNetMessageCodec.Frame(json)` → `FastBufferWriter.WriteBytesSafe`  
接收端：读取完整 buffer → `BattleNetMessageCodec.Unframe`（**不要**二次解析 length 字段）

消息名：`AetherboardBattleSync`（`BattleNetcodeService.MessageName`）

## 与 Python Host 的关系

Python `battle_host.py` 仍使用明文 JSON（TCP 行分隔 / WebSocket 文本帧）。  
NGO 正式传输层上线前，**NetcodeRelay 继续复用 WS 8769**，不破坏 Web/Unity 联机。

Host 可同时开启：

- Python WS 8769（Web 客户端）
- Unity NGO（VR 客户端经 UnityTransport）

## Quest 打包

```
Aetherboard → Configure Quest (Android) Build Settings
Aetherboard → Build Quest APK...
```

详见 [QUEST_BUILD.md](./QUEST_BUILD.md)。

## 测试

```bash
cd aetherboard/csharp/Aetherboard.Core.Tests && dotnet test
# NetMessageCodec_FrameRoundTrip
```
