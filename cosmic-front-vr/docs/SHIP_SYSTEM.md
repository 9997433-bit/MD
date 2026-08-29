# 战舰系统（P4）

## 概述

可玩护卫舰 **Aegis**：多人同舰职位协作，或单机自动登舰。

## 职位

| 职位 | 职责 | 操作 |
|------|------|------|
| **舵手 Pilot** | 驾驶船体 | WASD/摇杆移动，QE 转向 |
| **炮手 Gunner** | 手动炮塔 | 右摇杆瞄准，扳机射击 |
| **舰长 Captain** | 战术技能 | `V` 触发护盾过充 |
| **弹射 LaunchBay** | 放出机甲 | `L` 弹射出击 |

## 登舰 / 离舰

| 操作 | 键位 |
|------|------|
| 登舰（靠近战舰） | `B` 或 `F` |
| 离舰 | `X` |
| 机库直接登舰 | 生成方式选「战舰 — 舵手/炮手/舰长」 |

## 机库选项

生成方式下拉框：
1. 机甲出击
2. 战舰 — 舵手
3. 战舰 — 炮手
4. 战舰 — 舰长

选战舰职位后，战斗开始会自动登上己方 **Aegis**。

## 预制体

- `Assets/_Project/Prefabs/Warship_Aegis.prefab`
- `Assets/_Project/Prefabs/LaunchMech.prefab`（弹射用）

由 **Cosmic Front → Setup All Scenes** 生成。

## 场景集成

战斗地图含 `ShipSpawner`：
- 地球联合舰：玩家出生点附近
- 轨道联盟舰：对侧

## 网络

- `NetworkShipSync` + `NetworkHealthSync` + `NetworkTransform`
- `NetworkShipSpawner` 仅在 Server / 单机生成
- 登舰座位占用目前以本地为主；完整座位所有权同步可在后续迭代

## 数值（护卫舰）

| 参数 | 值 |
|------|-----|
| HP | 500 |
| 盾 | 200 |
| 最大航速 | ~8 m/s |
| 炮塔伤害 | 18 / 发 |
| 舰长技能 CD | 45s |
| 弹射 CD | 8s |

## 相关脚本

```
Assets/_Project/Scripts/Ship/
  ShipController.cs
  ShipMovement.cs
  ShipSeat.cs
  ShipGunnerTurret.cs
  ShipCaptainConsole.cs
  ShipLaunchBay.cs
  ShipCrewMember.cs
  ShipInput.cs
```
