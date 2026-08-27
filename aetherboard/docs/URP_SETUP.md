# URP 渲染管线设置

Aetherboard 已添加 **Universal Render Pipeline (URP) 14** 包，材质系统优先使用 `Universal Render Pipeline/Lit`，Built-in 管线自动回退 `Standard`。

## 一键配置

Unity Editor：

```
Aetherboard → Configure URP Pipeline
```

将创建并指派：

| 资源 | 路径 |
|------|------|
| URP Asset | `Assets/Aetherboard/Settings/AetherboardUniversalRP.asset` |
| Forward Renderer | `Assets/Aetherboard/Settings/AetherboardForwardRenderer.asset` |

默认 Quest 友好参数：

- MSAA 4x
- HDR 关闭
- 阴影距离 12m · 单级 Cascade
- 全局 Volume：`BattleVolumeProfile`（Bloom + 色彩调整 + 暗角）

## 后处理 Volume

`Configure URP Pipeline` 会创建：

| 资源 | 路径 |
|------|------|
| Volume Profile | `Assets/Aetherboard/Resources/Aetherboard/Settings/BattleVolumeProfile.asset` |

运行时由 `BattlePostProcessController` 自动挂载全局 Volume。Quest 构建会降级 Bloom 强度以保帧率。

手动微调：在 Project 窗口选中 `BattleVolumeProfile`，调整 Bloom Intensity / Vignette。

## 手动验证

1. `Edit → Project Settings → Graphics` — 确认 Scriptable Render Pipeline 已赋值
2. Play 模式检查桌台/棋子材质正常
3. Quest 构建前：`Player Settings → Color Space → Linear`（已由 Quest 向导设置）

## 与美术资源的关系

`BattleArtPalette` 自动选择 URP Lit shader。安装 Styled Prefab 后材质将使用 URP 着色器。

外部 FBX 导入建议：

- Material Creation Mode: **URP/Lit**
- 或在 Model Import → Materials 中勾选 **Use Material Description**

## 回退 Built-in

移除 `GraphicsSettings` 中的 URP Asset 即可恢复 Built-in 渲染；代码会自动回退 `Standard` shader。

## 相关菜单

- `Aetherboard → Configure Quest (Android) Build Settings`
- `Aetherboard → Install Battle Table Prefabs`
