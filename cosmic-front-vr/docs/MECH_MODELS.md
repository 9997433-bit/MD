# 目标机型一览

按 `docs/IP_BIBLE.md` 落地的可选用机体。机库会按阵营筛选。

## 型号表

| ID | 代号 | 名称 | 定位 | 可用阵营 | 技能 (V / VR 右 B) |
|----|------|------|------|----------|-------------------|
| `Kestrel` | MS-L1 | 迅影 | 轻型 | TU / OL / NF | 推进冲刺 |
| `Bastion` | MS-H1 | 重盾 | 重型 | TU / OL | 三重火力齐射 |
| `Warden` | NF-S1 | 守望 | 支援 | NF | 修复光束（友军/自身） |
| `Mediator` | NF-A1 | 仲裁 | 均衡 | NF | 相位护盾投射 |
| `Beacon` | NF-C1 | 航标 | 侦察 | NF | 传感器脉冲（刷新锁定） |

## 数值（摘要）

| 型号 | HP | 盾 | 速度 | 主武 DPS | 锁定距离 |
|------|----|----|------|----------|----------|
| Kestrel | 100 | 50 | 18 | 30 | 200 |
| Bastion | 200 | 80 | 12 | 45 | 180 |
| Warden | 110 | 70 | 14 | 18 | 160 |
| Mediator | 140 | 90 | 15 | 32 | 190 |
| Beacon | 80 | 40 | 20 | 22 | 260 |

完整常量见 `MechModelCatalog` / `docs/BALANCE_SHEET.md`。

## 外观

`MechVisualBuilder` 按型号生成占位剪影（窄肩推进器 / 宽肩盾炮 / 支援阵列 / 相位投射器 / 传感器碟），并叠加阵营主色。**无高达标志性造型。**

## 代码入口

- `MechModelId` / `MechModelCatalog`
- `MechController.SetModel`
- `MechSpecialAbility`
- 机库：`HangarMenu.RefreshMechOptions`（换阵营刷新列表）+ `HangarMechPreview` 旋转预览
- HUD：`CockpitHUD` 显示机型代号/中文名与专属技能冷却（键 **V** / VR 右 B）
