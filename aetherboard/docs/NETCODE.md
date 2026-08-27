# Unity Netcode 集成指南

Aetherboard 战斗同步已抽象为 `IBattleNetTransport`，并预留 Unity Netcode for GameObjects（NGO）接入点。

## 当前架构

```
BattleNetSession
  └── IBattleNetTransport
        ├── BattleTcpNetTransport        (8767)
        ├── BattleWebSocketNetTransport  (8769)
        └── BattleNetcodeRelayTransport  (NGO 就绪中继 → WS)
              └── BattleNetcodeService   (Custom Messaging 挂钩)
```

| 组件 | 作用 |
|------|------|
| `BattleNetMessageCodec` | 4 字节长度头 + UTF-8 JSON，兼容 NGO Custom Messaging |
| `BattleNetcodeRuntime` | 运行时检测 `Unity.Netcode` 程序集 |
| `BattleNetcodeService` | 发布/订阅战斗 JSON 消息 |
| `BattleNetcodeRelayTransport` | 客户端传输：当前走 WS，同时广播到 Service |

## 客户端传输模式

Unity HUD / `B` 键循环：

`Auto` → `WebSocket` → `TCP` → `NetcodeRelay` → `Auto`

**NetcodeRelay** 模式会创建 `BattleNetcodeService`，在 NGO 未安装时自动回退 WebSocket，与 Python Host 完全兼容。

## 安装 Unity Netcode（可选）

1. `Packages/manifest.json` 添加：

```json
"com.unity.netcode.gameobjects": "1.8.1",
"com.unity.transport": "2.3.0"
```

2. Host 场景添加 `NetworkManager` + `UnityTransport`
3. 在 `BattleNetcodeService.TryRegisterNetcodeHandlers` 中注册：

```csharp
// 伪代码 — NGO 安装后实现
CustomMessagingManager.RegisterNamedMessageHandler(
    BattleNetcodeService.BattleMessageName,
    (sender, data) => {
        var json = BattleNetcodeService.UnframeFromNetcode(data.ToArray(), data.Length);
        ReceiveBattleMessage(json);
    });
```

4. Host 广播 state 时：

```csharp
var bytes = BattleNetcodeService.FrameForNetcode(stateJson);
manager.CustomMessagingManager.SendNamedMessageToAll(
    BattleNetcodeService.BattleMessageName, bytes, NetworkDelivery.ReliableFragmentedSequenced);
```

## 与 Python Host 的关系

Python `battle_host.py` 仍使用明文 JSON（TCP 行分隔 / WebSocket 文本帧）。  
NGO 正式传输层上线前，**NetcodeRelay 继续复用 WS 8769**，不破坏 Web/Unity 联机。

## 测试

```bash
cd aetherboard/csharp/Aetherboard.Core.Tests && dotnet test
# NetMessageCodec_FrameRoundTrip
```
