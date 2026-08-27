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
PYTHONPATH=. python3 scripts/battle_host.py --port 8767 --boss earth --seed 42
```

## Unity 客户端

1. Play 进入战斗场景
2. HUD 点击 **Client**，或按 `N`（默认连接 `127.0.0.1:8767`）
3. 操作会发送到 Host；棋盘由 Host 广播的 `state` 更新

### 纯本地 Host（无 TCP）

- HUD 点 **Host** 或按 `H` — 使用 `BattleHostAuthority` 本地权威（不启动 Python 也可双人调试逻辑）

## C# 核心 API

```csharp
var host = new BattleHostAuthority("earth", 42);
var (ok, json, err) = host.ApplyCommand(cmd);

var replayed = BattleReplayer.Replay(commandLog);
```

## 后续

- WebSocket 封装（Quest / 浏览器）
- Unity Netcode 传输层替换 TCP
- 玩家身份与回合归属校验（Coop P1/P2）
