# Cosmic Front VR — Project Brief

## 一句话

原创宇宙战争题材的 **VR 多人对战平台**：玩家驾驶机甲或（后期）战舰，在三大阵营间进行团队对战。

## MVP 范围（P1–P3）

| 包含 | 不包含（后期） |
|------|----------------|
| 2 阵营、2 机甲型号 | 第 3 阵营 |
| 2 张地图（外壁 / 小行星带） | 可玩战舰 |
| 8v8 团队死斗 | Quest 移植 |
| PCVR（OpenXR / SteamVR） | 战役剧情 |
| 单机 + 局域多人原型 | 商业化商店 |

## 成功标准

1. VR 内连续游玩 20 分钟，测试者晕动反馈可接受（Snap Turn 默认开启）
2. 锁定 → 射击 → 击毁流程顺畅，PCVR ≥ 72 FPS
3. 4 人局域完成一整局 TDM，无崩溃
4. 全部资产与命名 **100% 原创**，无 GUNDAM / SEED 相关元素

## 技术栈

- Unity 2022.3 LTS + URP
- OpenXR + XR Interaction Toolkit
- Input System
- 网络（P2+）：Photon Fusion 或 Fish-Net（见 `docs/NETWORK_PLAN.md`）

## 仓库结构

```
cosmic-front-vr/
├── Assets/_Project/     # 游戏资源与脚本
├── docs/                # 设计文档
├── Packages/            # Unity 包依赖
└── ProjectSettings/
```

## 当前阶段

**P1 — 单机 VR 垂直切片**

交付：占位机甲 + 1 张地图 + AI 敌机 + 机库到结算完整循环。
