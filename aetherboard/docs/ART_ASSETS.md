# 美术资源指南

Aetherboard 支持三层视觉来源（自动回退）：

```
外部 FBX（Resources/Aetherboard/Art/Models/）
    ↓ 缺失时
Styled Prefab（Editor 菜单安装）
    ↓ 缺失时
运行时程序化几何体（PieceVisualBuilder / ProceduralAssets）
```

## 一键安装 Styled Prefab

Unity Editor：

```
Aetherboard → Install Battle Table Prefabs
```

生成内容：

| 资源 | 路径 |
|------|------|
| 格子 | `Resources/Aetherboard/GridCell.prefab` |
| 棋子 | `Resources/Aetherboard/PieceToken.prefab` |
| 桌台 | `Resources/Aetherboard/TableBase.prefab` |
| 预警环 | `Resources/Aetherboard/PreviewRing.prefab` |
| Boss 标记 | `Resources/Aetherboard/BossMarker.prefab` |
| 材质 | `Resources/Aetherboard/Materials/*.mat` |

棋子运行时按职业自动切换造型（`PieceVisualBuilder`）：

| 职业 | 造型 |
|------|------|
| 铁卫 Knight | 胶囊 + 盾片 |
| 白愈 WhiteMage | 法球 + 杖 |
| 黑炎 BlackMage | 尖帽 + 能量核 |
| 游弦 Bard | 柱体 + 琴面 |

## 替换为自定义 3D 模型

将 FBX / Prefab 放入：

```
Assets/Aetherboard/Resources/Aetherboard/Art/Models/
```

命名约定（**必须精确匹配**）：

| 文件名 | 用途 |
|--------|------|
| `Piece_Knight.prefab` | 铁卫棋子 |
| `Piece_WhiteMage.prefab` | 白愈棋子 |
| `Piece_BlackMage.prefab` | 黑炎棋子 |
| `Piece_Bard.prefab` | 游弦棋子 |
| `Table_Base.prefab` | 桌台底座 |
| `Grid_Cell.prefab` | 单格（可选） |

> 建议：模型高度约 **0.1m**，原点居中，面向 +Z。导入后拖成 Prefab 再放入 Models 目录。

`BattleArtCatalog` 会在运行时优先加载上述模型；缺失时回退到 Styled Prefab / 程序化造型。

## 调色板

`BattleArtPalette` 定义 FF14 风格配色，可在代码中调整金属度/光滑度：

- 桌台石色 / 金边
- 四职业主题色 + 发光预警

## 验证

1. 安装 Styled Prefab
2. Play → 日志应显示 `table=Prefab`
3. 切换 Boss / 移动棋子 → 职业造型与颜色正确
4. 放入 `Piece_Knight.prefab` 后重启 → 自动使用外部模型

## 性能（Quest）

- 当前 Styled Prefab 为低面数组合体（< 5000 tris 全桌）
- 外部模型建议：**< 2k tris / 棋子**，合并材质，ASTC 贴图
