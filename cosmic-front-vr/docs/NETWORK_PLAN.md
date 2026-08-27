# 多人网络规划（P2+）

## 阶段

| 阶段 | 方案 | 说明 |
|------|------|------|
| P2 原型 | Photon Fusion Host | 最快验证 4–8 人 |
| P3 测试 | Fusion Dedicated 或 Fish-Net | 降低 Host 优势 |
| P4 正式 | Dedicated Server + Steamworks | 反作弊、统计 |

## 同步原则

1. **Server Authoritative**：位置、HP、命中均由服务器裁定
2. **Client Prediction**：本地机甲移动预测，误差回滚
3. **Lag Compensation**：射击时 rewind 目标碰撞体
4. **不同步 VR 手指**：仅同步机体 Transform 与状态

## 待实现脚本占位

- `Assets/_Project/Scripts/Network/NetworkBootstrap.cs`
- `Assets/_Project/Scripts/Network/NetworkMech.cs`

P1 完成后再接入 Fusion SDK。
