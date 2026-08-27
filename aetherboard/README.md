# Aetherboard — FF14 风格 VR 互动战棋

从《最终幻想14：重生之境》战斗节奏提炼的 **GCD 战棋原型**：先以 Python 模拟 + 2D Web 验证玩法，再迁移到 Unity/OpenXR VR。

## 快速开始

### 1. 运行 Python 战斗模拟与测试

```bash
cd aetherboard
PYTHONPATH=. python3 -m unittest discover -s tests -q
PYTHONPATH=. python3 scripts/run_sim_demo.py
```

### 2. 启动 2D 可玩原型（浏览器）

```bash
cd aetherboard/web
python3 -m http.server 8765
```

打开 http://localhost:8765

## 项目结构

| 路径 | 说明 |
|------|------|
| `sim/` | 确定性战斗状态机（Python，可单元测试） |
| `web/` | 2D 浏览器原型（JS 引擎移植） |
| `tests/` | 棋盘、战斗流、Boss 机制测试 |
| `docs/GDD.md` | 策划文档：职业、阶段、机制 |
| `docs/VR_ROADMAP.md` | Unity VR 迁移路线 |

## 当前 MVP 内容

- **7×7 棋盘**，四职责小队：铁卫 / 白愈 / 黑炎 / 游弦
- **回合阶段**：预警 → 移动 → GCD → oGCD → 结算
- **两名 Boss**：
  - **土灵守护者**：重击 / 地震 / 缩圈 + 土神之怒
  - **风灵领主**：风刃 / 分散 / 集合 + 旋风
- **战术 AI**：自动躲避机制、打断读条、治疗与分散/集合
- **机制预警高亮**：Web 版棋盘显示危险区域预览

## 操作说明（Web）

1. 点击左侧小队成员选中
2. **移动阶段**：点击可达格子移动
3. **GCD / oGCD 阶段**：点技能按钮，再点目标格（治疗点友方，攻击点 Boss 格）
4. **结束当前阶段** 推进；未操作单位会自动使用默认技能
5. **自动演示一步** 快速观看 AI 对战

## 下一步（VR）

见 `docs/VR_ROADMAP.md`：Unity + OpenXR、桌面战棋桌、手柄抓取棋子与技能环。
