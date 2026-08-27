# 网络同步指南

Aetherboard 使用 **Host 权威** 模型：Host 运行战斗状态机，客户端只发送命令、接收状态快照。

## 协议

| type | 方向 | 说明 |
|------|------|------|
| `welcome` | Host → Client | `seed`, `bossId`, `coop` |
| `state` | Host → All | `payload` = 完整战斗状态 |
| `command` | Client → Host | `cmd` 含 `playerId`（双人模式） |
| `error` | Host → Client | `message` |

命令 `type`：`Move` | `Skill` | `EndPhase` | `SetBoss`

双人权限（`--coop`）：P1 = 铁卫/游弦，P2 = 白愈/黑炎

## 启动 Python Host

```bash
cd aetherboard
pip install -r requirements.txt
PYTHONPATH=. python3 scripts/battle_host.py --coop
```

| 端口 | 客户端 |
|------|--------|
| **8767** TCP | Unity Client |
| **8768** HTTP | Web（CORS 回退） |
| **8769** WebSocket | Web / Unity Client（推荐） |

## Web 浏览器联机

1. 启动 Host（`--coop` 开启双人校验）
2. `cd web && python3 -m http.server 8765`
3. P1：http://localhost:8765/?client=1&player=1
4. P2：http://localhost:8765/?client=1&player=2

WebSocket 默认 `ws://127.0.0.1:8769`；加 `&http=1` 强制 HTTP。

## Unity 客户端

1. Play → **Client**（`N`）连接 Python Host
2. 传输层（`B` 切换）：
   - **Auto**（默认）：WebSocket `8769` → TCP `8767` 回退
   - **WebSocket** / **TCP** 固定
3. 双人模式（`C`）+ 网络 P1/P2 按钮设置 `playerId`；Host `--coop` 时自动启用双人校验
4. **Host**（`H`）启动内置服务：
   - TCP `8767`（`BattleTcpHostServer`）
   - WebSocket `8769`（`BattleWebSocketHostServer`，Web 浏览器可直接联机）
5. Host 本地操作会自动广播 state 给所有已连接客户端

## C# API

```csharp
var host = new BattleHostAuthority("earth", 42, coop: true);
CoopRules.CanControl(playerId, unitId, coopEnabled);
```

## 后续

- Unity Netcode 传输层
- Quest 实机 WebSocket/TCP

## 命令回放

本地战斗会自动记录玩家命令（`BattleCommandLog`），格式与 Host 同步协议一致。

### Unity

| 快捷键 | 功能 |
|--------|------|
| **F6** | 导出 JSON 到剪贴板 + `persistentDataPath/aetherboard_last_replay.json` |
| **F7** | 从默认路径加载并回放 |

```csharp
director.ReplayFromCommandLogJson(json);
director.ExportCommandLogJson();
```

### Web（单机模式）

- **导出回放**：下载 JSON 并复制到剪贴板
- **回放当前记录** / **导入回放**：从文件重放命令序列

回放使用与 C# `BattleReplayer` 相同的确定性逻辑（相同 seed + bossId + 命令列表）。

## 传输层抽象

客户端连接通过 `IBattleNetTransport` 封装，当前实现：

| 实现 | 说明 |
|------|------|
| `BattleTcpNetTransport` | 行分隔 JSON（8767） |
| `BattleWebSocketNetTransport` | 消息帧 JSON（8769） |

`BattleNetTransportFactory` 可按类型创建，便于后续接入 Unity Netcode 适配器而不改动 `BattleNetSession`。

详见 [NETCODE.md](./NETCODE.md)。
