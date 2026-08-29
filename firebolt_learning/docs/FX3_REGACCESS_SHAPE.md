# FX3 寄存器访问「形态」（非 fabric 表）

> 目标：在仍不抓包的前提下，回答「软件怎么够到 FPGA 附近的控制窗」。  
> **不是** `FX3-REGMAP`（FPGA fabric 偏移表）的完成。

## 本轮确认

### 1. 关于 `0xE0011000`（已用 SDK 校正）

初始化函数 VA `0x4001250C` 确实以 **`0xE0011000`** 为基址写入多处偏移。  
但对照公开 `pib_regs.h`，该地址落在 **`rsrvd0[]` 保留空隙**（core 与 GPIF@`0xE0014000` 之间），**没有官方字段名**。

因此：

- “有写入” = 事实（disasm）
- “标准 PIB 配置块具名基址” = **撤回**；改见 `docs/FX3_PIB_CROSSREF.md`

具名、可对照 SDK 的锚点改为：

- `0xE0010000` PIB_CONFIG  
- `0xE0014000` GPIF_CONFIG  
- `0xE0018000` socket[]（步长 0x80）

### 2. Socket 步长（两套观察）

- 官方 DMA socket：`0xE0018000 + n×0x80`（固件含该基址字面量）
- 另见反汇编：`0xE0010000 + index<<4` 模式——**并存**，勿合并

### 3. 与 GPIF 官方区的关系

具名 GPIF 在 `0xE0014000`。学习路径仍是 GPIF/PIB → USB；同步不在 ARM。

### 3. 子系统标签（candidate）

在 `main.c` 字符串旁并列：`Op` / `Fpga` / `Fusion` / `Trace`，并靠近  
`State Machine handler` / `Counter Data Monitor handler`。  
可能是日志或状态机子系统枚举，**不能**直接当成 AI 采样 FSM。

### 4. GPIF/DMA 配置对象字段（candidate）

函数 `0x400113D0` 遍历的对象布局（`+0x00..+0x18`）见 JSON；解释为配置/描述符对象，而非通道采样表。

## 明确未完成

| 项 | 状态 |
|----|------|
| FPGA fabric 寄存器偏移（AIConv、channel、trigger） | **unknown** |
| Fusion bRequest → 上述 PIB 写的映射 | **unknown**（需抓包） |
| Signal Stream 帧布局 | **unknown** |

## 对学习目标的增量

同步仍在 ADC+FPGA；本轮补齐的是控制路径上的 **“第二跳窗口”**：

`Host/Fusion → FX3 → PIB(0xE0011000 / sockets) → GPIF → FPGA`

可读 `fx3_regaccess_shape.json` + `FX3_GPIF_PATH.md` + `DATA_PATH.md`。
