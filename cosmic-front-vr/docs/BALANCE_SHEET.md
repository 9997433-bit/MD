# Cosmic Front VR — 数值平衡表（P6）

> 从现有脚本默认值 / 预设读取并文档化。调参时优先改脚本字段或 `BalanceConfig`，再回写本表。  
> 源码锚点：`MechStatsPresets`、`MechController`、`Weapon*`、`Ship*`、`EscortFlagshipMode`、`CapturePointsMode`、`HealthSystem`、`GameManager`。

## 1. 机甲（Mech）

### 1.1 型号预设 — `MechModelCatalog`（目标机型）

| 参数 | Kestrel | Bastion | Warden | Mediator | Beacon |
|------|---------|---------|--------|----------|--------|
| HP | 100 | 200 | 110 | 140 | 80 |
| 盾 | 50 | 80 | 70 | 90 | 40 |
| 速度 | 18 | 12 | 14 | 15 | 20 |
| 主武 DPS | 30 | 45 | 18 | 32 | 22 |

兼容旧名：`MechStatsPresets.Light/Heavy` 仍映射到 Kestrel/Bastion。

### 1.1b 旧预设别名 — `MechStatsPresets`

| 参数 | Light→Kestrel | Heavy→Bastion | 建议区间 |
|------|---------------|---------------|----------|
| MaxHealth | 100 | 200 | Light 80–120 / Heavy 160–240 |
| MaxShield | 50 | 80 | Light 40–70 / Heavy 60–120 |
| MaxSpeed (m/s) | 18 | 12 | Light 15–22 / Heavy 9–14 |
| BoostFuel | 100 | 70 | Light 80–120 / Heavy 50–90 |

主武器 DPS 由 `MechController.ApplyModel` 注入（见上表）。

### 1.2 移动细节 — `MechMovement` 默认字段

| 参数 | 当前值 | 建议区间 | 备注 |
|------|--------|----------|------|
| acceleration | 35 | 25–45 | 手感响应 |
| verticalSpeed | 12 | 8–16 | 六向升降 |
| boostMultiplier | 1.8 | 1.4–2.2 | 相对 maxSpeed |
| drag | 2 | 1–3 | Rigidbody |
| yawRate (°/s) | 90 | 60–120 | |
| pitchRate (°/s) | 45 | 30–60 | |
| maxPitch (°) | 30 | 20–40 | |
| boostDrainPerSecond | 25 | 18–35 | |
| boostRegenPerSecond | 15 | 10–22 | |

### 1.3 主武器 — `WeaponPrimary`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| fireRate (发/秒) | 8 | 6–12 |
| damage（未 Configure 时） | 8 | 由 DPS/fireRate 推导 |
| range (m) | 150 | 120–200 |
| homingAssist | 0.15 | 0.05–0.30 |

有效单发伤害 ≈ `DPS / fireRate`（Light ≈ 3.75，Heavy ≈ 5.625）。

### 1.4 副武器 — `WeaponSecondary`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| fireCooldown (s) | 1.2 | 0.8–2.0 |
| maxAmmo | 4 | 2–6（GDD：轻型 2 / 重型 4，可按机型差异化） |
| reloadTime (s) | 4 | 3–6 |
| projectileSpeed | 40 | 30–60 |
| projectileDamage | 25 | 18–40 |
| fallback Raycast 距离 | 120 | 与主武器 range 对齐时可 120–150 |

### 1.5 锁定 — `LockOnSystem`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| lockConeDegrees | 15 | 10–25 |
| lockRange (m) | 200 | 150–280 |

### 1.6 弹道 — `Projectile`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| lifetime (s) | 5 | 3–8 |
| homingTurnRate (°/s) | 90 | 45–150 |

### 1.7 护盾回复 — `HealthSystem` 默认

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| shieldRegenDelay (s) | 3 | 2–5 |
| shieldRegenRate (/s) | 10 | 6–18 |

---

## 2. 战舰 Aegis（Ship）

### 2.1 船体耐久 — `ShipController.ApplyTeam`

| 船级 | HP | 盾 | 建议区间 |
|------|----|----|----------|
| Frigate（默认 Aegis） | 500 | 200 | HP 400–650 / 盾 150–280 |
| Cruiser（占位） | 800 | 300 | HP 650–1000 / 盾 250–400 |

场景向导默认也写 Frigate：`500 / 200`（`SceneSetupWizard`）。

### 2.2 航行 — `ShipMovement`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| maxSpeed | 8 | 6–12 |
| acceleration | 12 | 8–18 |
| verticalSpeed | 5 | 3–8 |
| yawRate | 35 | 25–50 |
| pitchRate | 20 | 12–30 |
| maxPitch | 20 | 15–30 |
| boostMultiplier | 1.4 | 1.2–1.8 |
| maxBoostFuel | 80 | 60–100 |
| boostDrain | 18 | 12–25 |
| boostRegen | 10 | 6–15 |

### 2.3 炮塔 — `ShipGunnerTurret`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| fireRate | 4 | 3–6 |
| damage | 18 | 12–28 |
| range | 220 | 180–280 |
| yawRate / pitchRate | 80 / 60 | ±20% |
| pitch 限制 | −20° ~ 40° | 按座舱视野微调 |

理论 DPS ≈ 72（18×4）。

### 2.4 舰长技能 — `ShipCaptainConsole`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| abilityCooldown (s) | 45 | 30–60 |
| shieldBoostAmount | 80 | 50–120 |
| abilityDuration (s) | 8 | 5–12 |

### 2.5 弹射舱 — `ShipLaunchBay`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| launchImpulse | 25 | 15–40 |
| cooldownSeconds | 8 | 5–12 |

---

## 3. 模式数值

### 3.1 团队死斗 TDM

| 参数 | 来源 | 当前值 | 建议区间 |
|------|------|--------|----------|
| matchDurationSeconds | `GameManager` / `NetworkScoreManager` | 600（10 min） | 300–900 |
| 击杀上限（设计） | GDD | 50 | 30–75（代码尚未硬限制，可后续加） |
| respawnDelaySeconds | `NetworkHealthSync` | 10 | 5–15 |
| 重生无敌（设计） | GDD | 3 s | 1–5（待实现） |

### 3.2 护送旗舰 Escort — `EscortFlagshipMode`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| cruiseSpeed | 4 | 2.5–6 |
| waypointReachDistance | 5 | 3–10 |
| 旗舰 HP / 盾 | 1200 / 400（`Configure`） | HP 900–1600 / 盾 300–600 |

旗舰过厚会拖长对局；过薄则护送方难有操作空间。建议以「进攻方 2–3 人机甲集火约 45–90 s」为基准试玩。

### 3.3 据点争夺 Domination — `CapturePoint` / `CapturePointsMode`

| 参数 | 当前值 | 建议区间 |
|------|--------|----------|
| radius | 12 | 8–18 |
| captureRate | 0.25（进度/秒，±1 满占） | 0.15–0.40 |
| 中立阈值 | \|progress\| < 0.05 → None | 0.03–0.10 |
| scoreTickInterval (s) | 2 | 1–3 |
| scoreLimit | 100 | 75–150 |

单点无人争夺时从 0 → 满占约 `1/captureRate` ≈ **4 s**。

---

## 4. AI / 刷怪

| 参数 | 来源 | 当前值 | 建议区间 |
|------|------|--------|----------|
| detectRange | `SimpleEnemyAI` | 120 | 80–160 |
| attackRange | `SimpleEnemyAI` | 60 | 40–80 |
| strafeStrength | `SimpleEnemyAI` | 0.6 | 0.3–1.0 |
| initialCount | `EnemySpawner` | 6 | 4–10 |
| respawnDelay | `EnemySpawner` | 8 | 5–15 |

---

## 5. VR Comfort（体验相关，非 DPS）

| 参数 | 来源 | 当前值 | 建议区间 |
|------|------|--------|----------|
| snapTurnAngle | `VRComfortSettings` | 45° | 30 / 45 / 90 |
| snapTurnEnabled | 同上 | true | 默认开 |
| vignetteOnBoost | 同上 | true | 可关 |
| Snap Turn cooldown | `VRSnapTurn` | 0.35 s | 0.2–0.5 |
| stickDeadzone | `VRMechInput` | 0.15 | 0.1–0.25 |

---

## 6. 粗略 TTK 参考（理论）

假设目标为 Light（HP 100 + 盾 50 = 150 EHP），无回复：

| 输出方 | 近似 DPS | 打穿 Light EHP |
|--------|----------|----------------|
| Light 主武 | 30 | ~5.0 s |
| Heavy 主武 | 45 | ~3.3 s |
| 副武单发 | 25 | 需配合主武 |
| 舰炮 | 72 | ~2.1 s |

盾回复（延迟 3 s 后 10/s）会拉长远程拉扯局；调 DPS 时同步观察护送旗舰（1600 EHP）被舰炮/机甲混合击沉时间。

---

## 7. 调参工作流

1. 改 `BalanceConfig` 或各组件 Inspector / 预设常量  
2. 单机：Light vs AI、Heavy vs 旗舰、据点 1v1 占点节奏  
3. 局域网 4v4：TDM 10 min 局、Escort 全程、Domination 先到 100  
4. 回写本表「当前值」列，保留建议区间备注  

集中常量见：`Assets/_Project/Scripts/Core/BalanceConfig.cs`（参考源；逐步接线，避免一次大改逻辑）。
