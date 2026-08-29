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
| 专属技能 | — | Secondary (B/Y) |
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

## 舒适度（VR Comfort）

组件：`VRComfortSettings`（挂在 XR Origin）+ 运行时菜单 `VRComfortMenu`。

| 选项 | 说明 | 默认 |
|------|------|------|
| Snap Turn | 右摇杆左右轻拨，按 `SnapTurnAngle`（默认 45°）瞬间转向 | 开启 |
| Smooth Turn | Snap 关闭时由机甲右摇杆连续 Yaw（`SmoothTurnSpeed` 供 Mech 侧参考；`VRSnapTurn` 不抢输入） | 关闭 |
| 暗角强度 `VignetteIntensity` | 冲刺时 `BoostVignette` 透明度（0–1） | 0.35 |
| 坐姿高度 `SeatedModeHeightOffset` | 相对 `CameraOffset` 的 Y 偏移（米） | 0 |
| 禁用平移 `DisableStrafeOption` | 关闭左右 strafing，仅前后移动 | 关闭 |

### 运行时切换

- 挂载 `VRComfortMenu` 后，键盘 **F1** 循环舒适档位（Snap/Smooth + 暗角强度）
- 也可调用 `ToggleSnapSmooth()` / `SetVignetteIntensity(float)` / `CyclePreset()`
- 编辑器 Inspector 可直接改 `VRComfortSettings` 字段

### 输入约定

- **Snap 开启**：`VRSnapTurn` 消费右摇杆水平 flick；机甲仍可读同轴做 pitch
- **Snap 关闭（Smooth）**：`VRSnapTurn` 早退，右摇杆完全交给 `VRMechInput` 连续转向，避免双重旋转
