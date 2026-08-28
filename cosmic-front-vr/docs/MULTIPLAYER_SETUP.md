# 多人联机搭建指南（P2 — Fish-Net LAN）

## 依赖

项目已通过 `Packages/manifest.json` 引入 **Fish-Net 4.5.8**。首次打开 Unity 时会自动从 GitHub 拉取，需保持网络畅通。

## 一键配置

1. Unity 菜单：**Cosmic Front → Setup All Scenes (Hangar + Battle)**
2. 确认 Hierarchy 中存在 **NetworkManager**（含 Tugboat 传输，端口 **7770**）
3. 确认 `Assets/_Project/Prefabs/NetworkPlayerMech.prefab` 已生成

## 局域网测试（两台 PC 或同一台开两个 Build）

### Host 端

1. 打开 `Hangar.unity` → Play
2. 选阵营 / 机甲
3. 点击 **Host 局域网**
4. 等待进入战斗地图

### Client 端

1. 打开游戏 Build 或第二个 Editor（Development Build）
2. 在地址栏输入 Host 的局域网 IP（如 `192.168.1.10`）
3. 点击 **Join 局域网**

> 同一台机器测试：`127.0.0.1`

## 架构说明

| 组件 | 职责 |
|------|------|
| `NetworkBootstrap` | Host / Client 连接，端口 7770 |
| `NetworkMatchManager` | 服务器生成玩家机甲，交替分配阵营 |
| `NetworkMechSync` | 仅 Owner 读输入；射击走 ServerRpc 服务器裁定 |
| `NetworkTransform` | 同步机甲位姿（Owner 驱动） |

## 同步策略（当前原型）

- **移动**：Owner 客户端驱动 + NetworkTransform 同步
- **射击**：Owner → ServerRpc → 服务器 Raycast/导弹伤害
- **VR 手部**：不同步，仅同步机甲 Transform
- **AI 敌机**：仅 Host/Server 本地刷新（Client 暂不共享 AI 状态）

## 防火墙

Windows 防火墙需允许 **UDP/TCP 7770** 入站，否则局域网 Join 失败。

## 常见问题

| 问题 | 处理 |
|------|------|
| 未找到 NetworkManager | 重新运行 Setup All Scenes |
| Client 连不上 | 检查 IP、防火墙、同一子网 |
| 玩家未生成 | 检查 DefaultPrefabObjects 是否含 NetworkPlayerMech |
| 远程机甲不动 | 确认 NetworkTransform 挂在玩家 Prefab 上 |

## 下一步（P3）

- Dedicated Server 无头构建
- 击杀榜网络同步
- AI 敌机服务器权威
- Steam Networking / Relay 穿透 NAT
