# Cosmic Front VR — P6 打磨上架路线图

> P5 已交付：Escort / Domination + Steam 离线骨架。  
> P6 目标：美术与手感打磨、数值平衡、Steam 正式接入与上架材料。  
> 配套：[BALANCE_SHEET.md](BALANCE_SHEET.md)、[STEAM_CHECKLIST.md](STEAM_CHECKLIST.md)

## 十条工作流 Checklist

### 1. 音效（SFX / 简易混音）

- [ ] 主武器脉冲、副武器发射 / 爆炸、命中反馈
- [ ] 推进 / 冲刺、护盾受击、机体爆炸
- [ ] 战舰：舵机嗡鸣、炮塔开火、弹射、舰长技能
- [ ] UI：机库确认、倒计时、胜负提示
- [ ] VR：空间音源挂点（驾驶舱 / 炮位）
- [ ] 总线：主音量 / SFX 滑条（可先挂机库）

### 2. 调校（机库 Loadout）

- [ ] GDD：3 个被动槽 UI 与存盘
- [ ] 示例被动：推进效率、盾回复、弹舱容量（数值进 [BALANCE_SHEET.md](BALANCE_SHEET.md)）
- [ ] 校验：不可叠出破坏 TTK 的组合
- [ ] 多人：Owner → ServerRpc 提交配装（见 NETWORK_PLAN）

### 3. 阵营（第三阵营维和舰队 NF）

- [ ] `TeamId` / 选人 UI 露出 Neutral（维和）
- [ ] 涂装主色：白 + 蓝（[IP_BIBLE.md](IP_BIBLE.md)）
- [ ] 出生点与记分板三方或「维和 vs 混战」规则定稿
- [ ] 专属轻/重机或通用机甲皮肤差分

### 4. Comfort（VR 舒适度）

- [ ] 设置页：Snap Turn 开/关、角度 30/45/90
- [ ] 推进 vignette 强度可调（`VRComfortSettings`）
- [ ] 可选：传送式复位、坐姿/站立身高校准说明
- [ ] 晕动测试：连续 20 min（Project Brief 成功标准）
- [ ] Steam VR 特性页文案与默认项一致

### 5. 护送 AI（Escort）

- [ ] 旗舰受击反应：减速 / 喊话事件 / 护航召唤
- [x] 进攻方 AI：优先集火旗舰权重（`EscortAttackWaveSpawner`）
- [x] 护送方 AI：拦截接近旗舰的敌人（`EscortDefenderWing`）
- [ ] 航点失败兜底（卡住、出界）
- [ ] 网络权威下进度与存活 SyncVar 回归测试

### 6. 据点 VFX（Domination）

- [x] 中立 / TU / OL / NF 占点环颜色与进度填充（`CapturePointVisual` + `CapturePointProgressRing`）
- [ ] 占领完成脉冲、积分得分飘字（可选）
- [ ] 距离外可辨识的柱光 / 全息标记（避免遮挡驾驶）
- [x] 与 `ModeStatusUI` 文案同步

### 7. 击杀 UI（Kill Feed / 结算）

- [ ] 击杀 Feed：杀手 → 武器/方式 → 受害者
- [ ] 自杀 / 环境击杀文案
- [ ] 连杀提示（可选）
- [ ] 结算页：个人 K/D、阵营分、模式特殊结果（护送成败 / 占点分）
- [ ] 多人与 `NetworkScoreManager` 数据对齐

### 8. Steam 深链（Deep Link / 邀请）

- [ ] 协议 `cosmicfront://join?ip=&port=` 注册（Windows）
- [ ] 冷启动与热启动解析进 Join 流程
- [ ] Overlay 邀请按钮调用 `GetInviteConnectString`
- [ ] 正式 AppID 下邀请与好友列表联调
- [ ] 失败提示：端口占用、版本不匹配

### 9. VFX（战斗通用特效）

- [ ] 枪口火焰、光束轨迹、导弹尾焰
- [ ] 护盾受击闪烁、击破爆炸（机甲 / 舰船分级）
- [ ] 冲刺尾迹、弹射分离特效
- [ ] URP 性能预算：中档 PC + VR 可维持目标帧率
- [ ] 禁止侵权剪影与配色（IP_BIBLE）

### 10. 数值平衡落地

- [ ] 按 [BALANCE_SHEET.md](BALANCE_SHEET.md) 完成首轮试玩调参
- [ ] （可选）接线 `BalanceConfig` 到 Mech/Ship/Mode
- [ ] 记录变更到平衡表「当前值」
- [ ] 上架前冻结一版「Release 候选」数值
- [ ] 对照 [STEAM_CHECKLIST.md](STEAM_CHECKLIST.md) 完成商店与构建项

---

## 建议推进顺序

```
Comfort + 击杀UI（体验可读）
  → 音效 + 战斗 VFX（反馈闭环）
  → 据点 VFX + 护送 AI（模式可读）
  → 调校 + 阵营（内容扩展）
  → 数值平衡冻结
  → Steam 深链 + 上架清单
```

## 完成定义（P6 Done）

1. 十条中核心体验项（1/4/7/9）可演示  
2. 平衡表有一版冻结数值  
3. Steam 正式 AppID 可初始化，商店页素材与隐私政策齐备  
4. IP 审查通过，无第三方商标资产  
