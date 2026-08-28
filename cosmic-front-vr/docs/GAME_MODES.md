# 游戏模式与 Steam（P5）

## 模式一览

| 模式 | 说明 | 胜利条件 |
|------|------|----------|
| **团队死斗 TDM** | 经典击杀分 | 时间到或分数领先 |
| **护送旗舰 Escort** | 地球联合护送旗舰沿航点航行，轨道联盟击沉 | 旗舰抵达终点 / 旗舰被毁 |
| **据点争夺 Domination** | 三据点 Alpha/Bravo/Charlie | 占点积分先到 100 或时间到领先 |

机库「模式」下拉框选择。

## 护送旗舰

- 组件：`EscortFlagshipMode`
- 旗舰沿 `EscortWaypoints` 自动巡航
- 护送方可登舰保护 / 用机甲护航
- 进攻方集火旗舰 HP（1200 + 盾 400）
- 右上角显示护送进度百分比

## 据点争夺

- 组件：`CapturePoint` + `CapturePointsMode`
- 据点内我方单位更多即可占领
- 占领后每 2 秒 +1 占点分
- 先到 100 分获胜

## Steamworks 与邀请深链（P5/P6）

`SteamManager`：
- **默认离线模式**（无需 Steamworks.NET 即可运行）
- 显示本机用户名
- 预留 `COSMIC_STEAMWORKS` 宏接入 Steamworks.NET
- `ParseJoinUrl` / `TryGetJoinEndpoint` 解析邀请深链为 IP + 端口

### 接入真实 Steam

1. 导入 [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET)
2. Player Settings → Scripting Define Symbols 添加 `COSMIC_STEAMWORKS`
3. 在 `SteamManager.Initialize` 中取消注释 `SteamAPI.Init()` 等调用
4. 申请正式 AppID 替换测试用 `480`（Spacewar）

### 邀请链接格式

```
cosmicfront://join?ip=192.168.1.10&port=7770
```

- **生成**：`SteamManager.GetInviteConnectString(ip, port)`；Host 成功后 `InviteCodePanel` 刷新并支持一键复制到剪贴板
- **解析**：`SteamManager.ParseJoinUrl(url, out ip, out port)`；实例上 `TryGetJoinEndpoint` 读取待处理邀请

### 启动深链（Client）

命令行参数：

```
-cosmicJoin=cosmicfront://join?ip=192.168.1.10&port=7770
```

`SteamInviteBootstrap` 读取该参数 → 自动填入机库地址栏 → 默认自动 Join（可在组件上关闭 `autoJoin`）。

## 相关脚本

```
Modes/EscortFlagshipMode.cs
Modes/CapturePointsMode.cs
Steam/SteamManager.cs
Steam/SteamInviteBootstrap.cs
UI/InviteCodePanel.cs
UI/ModeStatusUI.cs
```

## 测试步骤

1. **Setup All Scenes**
2. 机库选 **护送旗舰** → 单机开始
3. 观察旗舰沿航点移动；攻击旗舰可提前结束
4. 再测 **据点争夺**：飞入圆柱据点占领
