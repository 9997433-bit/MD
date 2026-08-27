# Aetherboard 更新日志

## [VR Milestone] — 2026-08

### 战斗核心
- C# `BattleEngine` 与 Python `sim/` 规则对齐，JSON Schema 同步
- 命令日志回放（F6/F7 / Web 导入导出）
- C# 单元测试 13 项 · Python 单元测试 19 项

### VR 交互
- 运行时自动场景 `RuntimeSceneBootstrap`
- 桌面键鼠 + IMGUI HUD + XR 抓取吸附
- 技能环 VR 射线、机制 VFX、读条打断 VFX
- Boss 全息 UI（3D 铭牌、土灵/风灵主题、轨道环）

### 美术
- Styled Prefab 安装器（桌台/格子/棋子/Boss 标记）
- `PieceVisualBuilder` 四职业造型 + 外部 FBX 钩子
- `BattleArtPalette` FF14 风格材质

### 网络
- Host 权威同步（TCP 8767 / WS 8769 / NGO 7777 三路并行）
- `IBattleNetTransport` 可插拔传输
- NGO CustomMessaging + UnityTransport 原生客户端
- VR 联机面板 + Host IP PlayerPrefs 持久化

### Quest
- APK 构建/侧载 Editor 菜单
- 实机诊断日志 + `QUEST_VERIFICATION.md` 验收清单
- Quest 性能/光照优化配置

### 音频
- 程序化音效：阶段/伤害/治疗/读条/打断
- Boss 主题和弦、读条紧迫滴答、联机连接提示音
- 胜利琶音 / 失败下行滑音

### 渲染与触觉
- URP 14 可选迁移 + Editor 一键配置
- Quest/PCVR 控制器触觉：抓取、落子、技能
- 战斗结算世界空间面板（胜败统计、再战/换 Boss）

### 文档
- `VR_ROADMAP.md` · `NETCODE.md` · `ART_ASSETS.md` · `URP_SETUP.md` · `QUEST_BUILD.md` · `QUEST_VERIFICATION.md`
