# Dedicated Server 指南（P3）

## 构建无头服务器

Unity 菜单：**Cosmic Front → Build → Dedicated Server (Windows Headless)**

输出：`Builds/Server/CosmicFrontServer.exe`

## 启动服务器

```bash
CosmicFrontServer.exe -batchmode -nographics -cosmicServer
```

可选指定地图（需在 DedicatedServerBootstrap 中配置 `battleScene` 字段，或后续扩展 `-cosmicMap` 参数）。

服务器会：
1. 启动 Fish-Net Server（端口 **7770**）
2. 自动载入默认战斗地图
3. 等待客户端 Join

## 客户端连接

1. 打开 VR 客户端（Editor Play 或 Build）
2. `Hangar.unity` → 输入 **Dedicated Server IP**
3. 点击 **Join / Dedicated**

## P3 网络功能

| 功能 | 说明 |
|------|------|
| `NetworkScoreManager` | 阵营分、个人 K/D、比赛计时同步 |
| `NetworkHealthSync` | 服务器权威 HP，10 秒复活 |
| `MatchScoreboardUI` | 左上角实时记分板 |
| `Map_AsteroidField` | 第二张地图（碎屑航道） |

## 防火墙

开放 **UDP/TCP 7770**。

## Linux 服务器（手动）

1. Build Target 改为 Dedicated Server Linux
2. 同样附加 `-cosmicServer` 启动

## 调试

- 服务器日志：`[DedicatedServer]`、`[NetworkBootstrap]` 前缀
- 客户端记分板应显示 `TU x | OL y` 阵营分
