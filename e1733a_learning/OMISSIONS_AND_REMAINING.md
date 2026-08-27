# 遗漏登记与剩余边界

**更新时间**：2026-08-27（第五轮补登后）  
**账本规模**：307 条 identifier

本文档列出：**本轮已补**、**仍建议后续补（candidate）**、**明确不做（保持 unknown/forbidden）** 三类内容，供毕设写作与下一步学习对照。

---

## 一、第五轮已补（+73 条）

| 类别 | 条数 | identifier 前缀 | status |
|------|------|-----------------|--------|
| CC_READSTATUS 状态查询 | 29 | `ACQ-E1-STATUS-*` | E1 |
| 测量类型 SingleAxis | 1 | `ACQ-E1-MEATYPE-SINGLE` | E1 |
| 分析视图入口 | 2 | `ANA-E1-VIEW-*` | E1 |
| AnaGraph Comprise 位 | 10 | `ANA-E1-GRAPH-*` | candidate |
| AnaNum Comprise 位 | 10 | `ANA-E1-NUM-*` | candidate |
| ISO Information 报告字段 | 8 | `ANA-E1-STD-ISOFIELD-*` | candidate |
| ISO 不确定度 UI 字段 | 5 | `ANA-E1-UNC-*`（补全 7 条合计） | candidate |
| VDI 算法体槽 | 1 | `ANA-UNK-ALG-VDI-BODY` | unknown |
| CC_SAVE TXT/RUN 子类型 | 5 | `FMT-SAVE-*_TXT/RUN` | E1 forbidden_writer |
| 时基原始数据尾块 | 1 | `FMT-TBRAWDATA-SECTION` | candidate |
| 55291A 禁止边界 | 1 | `CMP-FORBID-55291A-BINARY` | forbidden_writer |

---

## 二、仍建议后续补（非阻塞，Remote.h 有锚点）

| 类别 | 估计条数 | 说明 |
|------|----------|------|
| MEASETUP 测量配置主体 | ~43 | Cycles/Points/Interval/StartPos 等；已在 `sample_field_index.json` 191 字段中覆盖，账本 identifier 化可选 |
| ISOSETUP 报告元数据其余字段 | ~22 | Operator/MachineName/FeedRate 等；大纲标为「不做」UI 元数据，可按需 candidate |
| CC_SELECTUPPERDISP / CC_ERASE / CC_SETUP 子项 | ~20 | 采集 UI 通道选择与数据擦除 |
| CC_PRINT 报告标准子项 | 7 | ISO1988/1997/2006/2014/GB2000 等 |
| CC_OPEN 合并数据入口 | 4 | MERGEDATA/COMBINED/PAR/SQU |
| TIMSETUP / SYSSETUP / XDASETUP | ~25 | 时基与系统/双轴配置 |
| CMP-E1-ENV-CAL 校准对话框 | 3–5 | 仅 English.csv 字符串，无 Remote.h 锚点 |
| INFSETUP 报告元数据 | 9 | 明确不做，除非论文需要 UI 地图 |

---

## 三、明确不做（保持现状）

### 函数体 / 算法（unknown，禁止升级 E1）

- `E1735ACore_ProcessRawData` — 激光测距公式（Edlén/Ciddor）
- `E1736A_ReadEnvironment` / `CMP-UNK-AMBIENT-BODY` — 环境补偿算法体
- `CMP-UNK-INTERPOLATE-ALG` — 样条插值
- `ANA-UNK-ALG-ISO230-BODY` / `ANA-UNK-ALG-VDI-BODY` — 标准算法实现

### 无 RTTI（Delphi 文档类）

- `ACQ-UNK-DELPHI-COLLECTDOC` + 13× `ANA-UNK-DELPHI-*DOC`

### 强制 null 桥（7 条，proven_bridge 永为 null）

见 `bridge_matrix.json`：LTB→速度公式、Ambient→LaserDist 同路径、Interpolate→样条、START→任务实例、E4→厂商 FSM、LinearErr→CC_ANALYSIS 实现、Wavelength→Edlén/Ciddor。

### forbidden_writer（2 条）

- `CMP-FORBID-CNC-WRITER`
- `CMP-FORBID-55291A-BINARY`

### 附录层（非三块核心）

- USB 驱动 IOCTL、Setup.exe 安装流程、多语言 CSV 全文、Automation.pdf 动态演示

---

## 四、Sample 解析已知例外（已登记，非账本遗漏）

| 项 | 位置 | 状态 |
|----|------|------|
| `Axis` 字段 DIAGONAL 为 ItemText | `sample_field_index.json` cross_sample_value_type_exceptions | 已注记 |
| `<Time Base Raw Data>` ODF 外尾块 | `sample_field_index.json` unindexed_sections + `FMT-TBRAWDATA-SECTION` | 已 candidate |
| `has_linear_err=false` 表示值为空 | `sample_manifest.json` schema_notes | 已澄清 |

---

## 五、动态层（毕设下一步，不在静态包范围）

1. 手算 `Sample.Lin` 的 `LinearErr` → 对照 `CC_ANALYSIS` CI 0–11 返回值
2. Demo Mode 下 Remote 消息动态验证（READERRORDATA / ANALYSIS）
3. 直驱三轴龙门动态模型辨识与测量链集成

---

## 六、停止条件（第五轮后仍满足）

| # | 条件 | 结果 |
|---|------|------|
| 1 | 三块目录无空 identifier | ✅ 307 条 |
| 2 | 无新指令窗仍为 unknown | ✅ |
| 3 | 7 条强制 null 桥 | ✅ |
| 4 | forbidden_writer | ✅ ×2 |
| 5 | 无冒充厂商状态机 | ✅ |

**声明**：目录更完整 ≠ 厂商软件等价 ≠ 掌握运行行为。
