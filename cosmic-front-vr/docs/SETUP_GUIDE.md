# Cosmic Front VR — 本地搭建指南

## 第一步：安装 Unity

1. 下载 [Unity Hub](https://unity.com/download)
2. 安装 **Unity 2022.3 LTS**
3. 模块勾选：**Windows Build Support (IL2CPP)**、如需 VR 再装对应平台

## 第二步：打开项目

```bash
git clone <你的仓库地址>
```

Unity Hub → Open → 选择 `cosmic-front-vr` 文件夹。

首次打开会下载 URP、OpenXR、Input System 等包，需等待数分钟。

## 第三步：Input System

弹出对话框时选择 **Input System Package (New)** → Restart。

## 第四步：生成试玩场景

Unity 菜单：**Cosmic Front → Setup P1 Prototype Scene**

打开 `Assets/_Project/Scenes/Map_ColonyRim.unity`，点击 **Play**。

## 第五步：键鼠试玩

见根目录 `README.md` 键位表。目标：移动、锁定（Tab）、击毁敌机。

## 第六步：接入 VR（可选）

1. **Edit → Project Settings → XR Plug-in Management**
   - PC 平台勾选 **OpenXR**
   - 按头显安装对应 Runtime（SteamVR / Meta Link 等）

2. **Window → Package Manager** 确认已安装 XR Interaction Toolkit

3. 从 Samples 导入 **Starter Assets → XR Origin**

4. 场景中：
   - 删除或禁用 Main Camera
   - 放入 XR Origin
   - 添加 `PlayerMechBinder`，绑定 PlayerMech 与 CockpitAnchor

5. Play with VR headset connected

## 第七步：Build Settings

1. **File → Build Settings**
2. Scenes 加入 `Map_ColonyRim`（及后续 Hangar）
3. Platform: **Windows**
4. **Player Settings → XR Plug-in Management** 确认 OpenXR

## 常见问题

| 问题 | 处理 |
|------|------|
| 包解析失败 | 确认 Unity 版本为 2022.3.x |
| 敌机不刷新 | 重新运行 Scene Setup Wizard |
| 无法锁定 | Tab 按住；确保敌机在准星 15° 锥形内 |
| VR 晕 | 启用 `VRComfortSettings` Snap Turn |

## 下一步（P2）

1. 安装 Photon Fusion 或 Fish-Net
2. 实现 `Network/NetworkBootstrap.cs` 中的房间逻辑
3. 为 `MechController` 添加网络同步组件

详见 `docs/NETWORK_PLAN.md`。
