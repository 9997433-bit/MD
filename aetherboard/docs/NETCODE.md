# Unity Netcode 集成指南

Aetherboard 战斗同步已抽象为 `IBattleNetTransport`，并完成 Unity Netcode for GameObjects（NGO）**原生 UnityTransport** 传输层。

## 当前架构

```
BattleNetSession
  └── IBattleNetTransport
        ├── BattleTcpNetTransport        (8767)
        ├── BattleWebSocketNetTransport  (8769)
        ├── BattleNetcodeRelayTransport  (WS + NGO 侧车，兼容 Python Host)
        └── BattleNetcodeNativeTransport (NGO UnityTransport，端口 7777)

NGO 层（com.unity.netcode.gameobjects）
  ├── BattleNetcodeFacade           CustomMessaging 同步/命令双通道
  ├── BattleNetcodeNativeBridge     运行时 NetworkManager + UnityTransport
  ├── BattleNetcodeHostCoordinator  Host 握手 + 命令入口
  └── BattleNetcodeNGOSetup         自动挂载 Coordinator
```

| 组件 | 作用 |
|------|------|
| `BattleNetMessageCodec` | 4 字节长度头 + UTF-8 JSON |
| `BattleNetcodeNativeTransport` | 客户端：StartClient + 命令/状态 CustomMessaging |
| `BattleNetcodeNativeBridge` | 运行时创建 NetworkManager，StartHost/StartClient |
| `BattleHostCommandProcessor` | TCP/WS/NGO 共享 Host 命令校验与应用 |
| `BattleNetcodeFacade` | `AetherboardBattleSync`（状态）+ `AetherboardBattleCommand`（命令） |

## 客户端传输模式

Unity HUD / `B` 键循环：

`Auto` → `WebSocket` → `TCP` → `NetcodeRelay` → **`NetcodeNative`** → `Auto`

| 模式 | 协议 | 端口 | 说明 |
|------|------|------|------|
| Auto | WS → TCP | 8769 / 8767 | 兼容 Python / Web |
| NetcodeRelay | WebSocket | 8769 | 旧中继，侧车 NGO Service |
| **NetcodeNative** | UnityTransport | **7777** | 原生 NGO，无 WS 依赖 |

## Host 模式

按 `H` 开启 Host 时，默认同时启动：

- TCP `8767`
- WebSocket `8769`
- **NGO UnityTransport `7777`**（需 manifest 含 NGO 包）

`PublishHostState()` 经三路广播；NGO 客户端连接后自动收到 `welcome` + 初始 `state`。

## 安装 Unity Netcode

`Packages/manifest.json` 已包含：

```json
"com.unity.netcode.gameobjects": "1.8.1",
"com.unity.transport": "2.3.0"
```

Editor 菜单：

- `Aetherboard → Netcode → Verify NGO Packages`
- `Aetherboard → Build Quest APK...`

### 手动场景（可选）

也可在场景中预置 `NetworkManager` + `UnityTransport`；运行时桥接会复用已有实例。

## 与 Python Host 的关系

Python `battle_host.py` 仍使用明文 JSON（TCP / WebSocket）。  
Web 客户端继续走 WS 8769；Unity VR 客户端可选用 **NetcodeNative 7777** 直连 Unity Host，互不干扰。

## 测试

```bash
cd aetherboard/csharp/Aetherboard.Core.Tests && dotnet test
# NetMessageCodec_FrameRoundTrip
```

## 联机速查

```bash
# Unity Host：Play → H（TCP + WS + NGO）
# Unity Client：N，B 切到 NetcodeNative，hostAddress = Host IP

# 或 Python Host（Web / Relay 客户端）
PYTHONPATH=. python3 scripts/battle_host.py --coop
```
