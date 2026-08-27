# VR 迁移路线

## 技术栈

- **引擎**：Unity 2022 LTS+
- **XR**：OpenXR（Meta Quest + PCVR）
- **网络（后期）**：Host 权威回合状态同步

## 架构

```
VR Client (Unity)
  ├── TableView      # 虚拟战棋桌、棋子物理/吸附
  ├── InputLayer     # 抓取、指向、快捷 oGCD
  ├── VFX/UI         # Telegraph 圈、读条条
  └── BattleClient   # 发送 ActionChoice，接收 BattleState

Battle Sim (C# 或共享 JSON Schema)
  └── 与 aetherboard/sim Python 规则对齐
```

## 迁移步骤

1. **规则对齐**：将 `sim/types.py` 结构导出为 JSON Schema，Unity 侧实现相同状态机
2. **桌面场景**：7×7 格子、4 棋子模型、Boss 全息投影
3. **交互**：XR Grab + Snap Grid；GCD 技能环在棋子旁展开
4. **机制 VFX**：重击红圈、地震裂纹、缩圈光墙、读条条
5. **舒适选项**：坐/站模式、转向快照、简化 oGCD 菜单

## 首版 VR 范围

- 单人 vs 土灵守护者
- 1 张桌台场景
- 3 个 Boss 机制 VFX
- 无在线多人

## 参考项目

- *Demeo* — VR 桌游交互
- *Tabletop Simulator VR* — 抓取与骰子
- FF14 ARR 极神 — 机制可读性
