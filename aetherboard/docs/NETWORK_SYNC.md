# 网络同步指南

Aetherboard 使用 **Host 权威** 模型：Host 运行战斗状态机，客户端只发送命令、接收状态快照。

## 协议

每行一条 JSON（换行分隔，适合 TCP）：

| type | 方向 | 说明 |
|------|------|------|
| `welcome` | Host → Client | `seed`, `bossId` |
| `state` | Host → All | `payload` = 完整战斗状态（对齐 `schema/battle_state.schema.json`） |
| `command` | Client → Host | `cmd` = `{type, unitId, skillId, targetX, targetY, bossId}` |
| `error` | Host → Client | `message` |

命令 `type` 取值：`Move` | `Skill` | `EndPhase` | `SetBoss`

## 启动 Python Host（LAN 测试）

```bash
cd aetherboard
PYTHONPATH=. python3 scripts/battle_host.py --port 8767 --http-port 8768 --boss earth --seed 42
```

| 端口 | 客户端 |
|------|--------|
| **8767** TCP | Unity Client 模式 |
| **8768** HTTP | Web 浏览器（CORS 已开启） |

## Web 浏览器联机

1. 启动 Host（见上）
2. `cd web && python3 -m http.server 8765`
3. 打开 http://localhost:8765/?client=1
4. 操作通过 HTTP 发往 Host，棋盘由返回的 `state` 更新

可选：`?client=1&host=http://192.168.1.10:8768`

## Unity 客户端

1. Play 进入战斗场景
2. HUD 点击 **Client**，或按 `N`（默认连接 `127.0.0.1:8767`）
3. 操作会发送到 Host；棋盘由 Host 广播的 `state` 更新

### 纯本地 Host（Unity 内置 TCP）

- HUD 点 **Host** 或按 `H` — 自动启动 `BattleTcpHostServer`（端口 8767）
- 另一台 Unity 实例选 **Client** 连接同一局域网 IP

### Python Host（Web + Unity）

- 运行 `battle_host.py` — TCP 8767 + HTTP 8768

## C# 核心 API

```csharp
var host = new BattleHostAuthority("earth", 42);
var (ok, json, err) = host.ApplyCommand(cmd);

var replayed = BattleReplayer.Replay(commandLog);
```

## 后续

- WebSocket 长连接（替代 HTTP 轮询）
- Unity Netcode 传输层替换 TCP
- 玩家身份与回合归属校验（Coop P1/P2）
