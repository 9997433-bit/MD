# FX3 寄存器访问「形态」（非 fabric 表）

> 目标：在仍不抓包的前提下，回答「软件怎么够到 FPGA 附近的控制窗」。  
> **不是** `FX3-REGMAP`（FPGA fabric 偏移表）的完成。

## 本轮确认

### 1. PIB 配置块 `0xE0011000`

初始化函数 VA `0x4001250C` 的字面量基址为 **`0xE0011000`**，并对该基址执行一串 `str`：

典型偏移（见 `manifests/fx3_regaccess_shape.json`）：  
`0x04, 0x0C, 0x10, 0x38, 0x3C, 0x48–0x54, 0x60–0x6C, 0x70–0x8C, …`

含义：这是 **FX3 片上 PIB/GPIF 引擎配置**，用于把 socket/总线参数设好，以便 FPGA 侧 GPIF-II 数据通路工作。

### 2. 与 `0xE0010000 + index<<4` 的关系

- `0xE0010000 + n*16`：按 socket 索引的寄存器窗（已 confirmed）
- `0xE0011000`：更偏 **全局/块级配置** 基址（本轮 confirmed）

二者同属 PIB 族，共同构成 FX3→FPGA 桥的 MMIO 面。

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
