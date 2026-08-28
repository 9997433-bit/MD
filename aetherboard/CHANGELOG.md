# Aetherboard 更新日志

## [0.4.0-vr] — 2026-08-28

### 第四 Boss：火灵君主
- 新机制：**火息**（对角线 X）、**陨石**（3 落点锁定）、**灼热连结**（必须与友军相邻）、**喷发**（2 回合读条可打断）
- Python / C# Core / Web / JSON Schema 规则对齐
- VR：Boss 选择第四按钮、HUD 快捷键 `4`、火主题全息/VFX/粒子/音效
- Web：Boss 下拉新增火灵君主

## [0.3.1-vr] — 2026-08-27

### 发布
- PR #10 合并至 `main`
- Git 标签：`v0.3.1-vr`

### 三 Boss 抛光
- **冰主题音效**：Boss 切换和弦 + 读条滴答频率区分土/风/冰
- **读条 VFX**：`FuryCastBarVFX` 冰灵配色与打断爆发
- **Quest 验收**：自动检查三 Boss 注册 + 手册项 #11（Boss 切换）
- 操作提示 / README / GDD / VR_ROADMAP 同步三 Boss 范围

## [0.3.0-vr] — 2026-08-27

### 发布
- PR #9 合并至 `main`
- Git 标签：`v0.3.0-vr`

### 第三 Boss：冰灵女皇
- 新机制：**冰枪**（十字路径）、**霜冻**（2×2 锁定危险区）、**冰环**（距中心曼哈顿距离=2）、**暴雪**（2 回合读条可打断）
- Python / C# Core / Web / JSON Schema 规则对齐
- VR：Boss 选择面板第三按钮、HUD 快捷键 `3`、冰主题全息/VFX/粒子
- Web：Boss 下拉新增冰灵女皇

## [0.2.2-vr] — 2026-08-27

### VR UX
- **Boss 选择持久化**（`BattleBossPrefs`）— Quest 重启记住上次 Boss
- Editor 菜单 `Reset Controls Hint` 重新显示操作提示

## [0.2.1-vr] — 2026-08-27

### VR UX（Phase 2）
- 世界空间 **Boss 选择面板**（桌台左侧，Quest 无需键盘）
- 首次启动 **操作提示** 面板（PlayerPrefs 记住关闭状态）
- Quest 验收报告增加 BossSelectPanel 检查

## [0.2.0-vr] — 2026-08-27

### 发布
- PR #5 合并至 `main`
- Git 标签：`v0.2.0-vr`

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
- URP 后处理 Volume（Bloom / 色彩调整 / 暗角，Quest 自动降级）
- FBX 导入向导 + 美术资源清单校验
- Quest 验收工具链（预检、报告导出、`scripts/quest_verify.sh`）
- Quest/PCVR 控制器触觉：抓取、落子、技能
- 战斗结算世界空间面板（胜败统计、再战/换 Boss）

### 文档与工具
- `VR_ROADMAP.md` · `NETCODE.md` · `ART_ASSETS.md` · `URP_SETUP.md` · `QUEST_BUILD.md` · `QUEST_VERIFICATION.md`
- 首次设置向导 · `run_all_tests.sh` · `release_preflight.sh` · `quest_verify.sh`
- 版本标记：`VERSION`（`0.2.0-vr`）
