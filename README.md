# Keysight E1733A 1.14.1 学习与静态分析仓库

本仓库包含 **原始安装包**、**解包 payload（53 文件）** 与 **E1733A 干涉仪程序静态分析学习包**。

## Cosmic Front VR（VR 游戏项目）

独立 Unity 项目位于 [`cosmic-front-vr/`](cosmic-front-vr/README.md) — 原创宇宙战争 VR 对战平台（P1 单机原型阶段）。

## 目录结构

| 路径 | 说明 |
|------|------|
| `Install Keysight E1733A 1.14.1 (Win64).exe` | 原始安装包（Wextract + LZX CAB） |
| `extracted/` | 解包后的 53 个文件（exe/dll/Sample.*/Remote.h/PDF 等） |
| `e1733a_learning/` | 静态分析学习包（账本 307 条、catalog、测试、manifest） |
| `device_learning/` | USB/FPGA 设备位流+照片静态学习包（237 条 identifier、70 pytest） |
| `浙大/资料/是德科技/` | 中文大纲、静态分析报告、Remote.h 副本 |

## 快速开始（device_learning）

```bash
cd device_learning
make verify
make health
```

详见 `device_learning/HARDWARE_HANDOFF.md`（实机接入）。

## 快速开始（e1733a_learning）

```bash
cd e1733a_learning
python3 scripts/generate_ledger.py
PYTHONPATH=. python3 -m pytest tests/ -q
```

## 核心产物

- `e1733a_learning/EvidenceLedger.json` — 采集/分析/补偿/格式 四块 identifier 账本
- `e1733a_learning/OMISSIONS_AND_REMAINING.md` — 遗漏登记与剩余边界
- `浙大/资料/是德科技/E1733A_静态分析报告.md` — 首份静态分析报告
- `浙大/资料/是德科技/E1733A_采集分析补偿_静态分析大纲.md` — 完整分析大纲

## 声明

目录完整 ≠ 厂商软件等价 ≠ 掌握运行行为。`ProcessRawData` / 环境补偿 / 插值算法体保持 `unknown`。
