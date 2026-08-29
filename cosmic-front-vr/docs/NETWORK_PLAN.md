# 多人网络规划

## 当前阶段（P2 ✅）

| 项目 | 方案 |
|------|------|
| 网络库 | **Fish-Net 4.5.8** |
| 连接方式 | LAN Host / Join（Tugboat，端口 7770） |
| 权威 | 服务器裁定射击伤害；Owner 驱动移动 |
| 玩家生成 | `NetworkMatchManager` Server Spawn |

详见 [MULTIPLAYER_SETUP.md](MULTIPLAYER_SETUP.md)

## 后续阶段

| 阶段 | 方案 | 说明 |
|------|------|------|
| P3 测试 | Dedicated Server Build | 独立服务器，客户端仅连接 |
| P4 正式 | Steamworks + FishySteamworks | 好友邀请、NAT |
| P5 | Lag Compensation | 射击 rewind 碰撞体 |

## 同步原则

1. **Server Authoritative 伤害**：命中在 ServerRpc 中执行
2. **Owner 驱动移动**：NetworkTransform 从 Owner 同步
3. **不同步 VR 手指**：仅机体 Transform
4. **Loadout**：Owner 通过 ServerRpc 提交阵营/机甲选择

## 核心脚本

- `Network/NetworkBootstrap.cs` — 连接入口
- `Network/NetworkMatchManager.cs` — 房间与生成
- `Network/NetworkMechSync.cs` — 玩家机甲网络层
- `Network/NetworkSessionConfig.cs` — 端口与人数常量
