# VR 操作说明

## 手柄映射（OpenXR 通用）

| 操作 | 左手控制器 | 右手控制器 |
|------|------------|------------|
| 平移 | 摇杆 | — |
| 机体 Yaw / Pitch | — | 摇杆 |
| 主武器（脉冲束） | — | 扳机 (Trigger) |
| 副武器（导弹） | 扳机 | — |
| 锁定目标 | Grip 或侧键 | Primary (A/X) 也可切换 |
| 推进冲刺 | 摇杆按下 | — |
| Snap Turn（舒适转向） | — | 摇杆快速左右拨 |

## 编辑器键鼠（无头显时自动切换）

见根目录 `README.md` 键位表。

## 输入自动切换

`MechInputRouter` 检测到 VR 头显时启用 `VRMechInput`，否则使用 `FallbackMechInput`。

## OpenXR 配置

1. **Edit → Project Settings → XR Plug-in Management**
2. PC 标签页勾选 **OpenXR**
3. 安装对应 Runtime（SteamVR / Oculus / Windows Mixed Reality）

## 与 XRI Starter Assets 的关系

当前使用轻量自研 `XROriginSetup`（不依赖 XRI 样例预制体）。  
若已导入 **XR Interaction Toolkit → Starter Assets**，可将 `XROrigin` 预制体替换自研 Rig，保留 `PlayerMechBinder` 与 `VRSnapTurn` 组件即可。

## 舒适度

- 默认开启 Snap Turn（45°），可在 `VRComfortSettings` 组件上关闭
- 冲刺时屏幕暗角（`BoostVignette`）减轻晕动
