# FX3 角色地图：配置代理 + DMA 桥（同步不在 ARM）

> 目录完整 ≠ 厂商等价 ≠ 掌握运行行为
>
> 阶段：`static_deep_no_capture`（纯静态字节/字符串分析，不抓包、不反编译）
> 证据来源：`manifests/fx3_deep.json`（由 `scripts/analyze_fx3_deep.py` 生成）
> 对象：`firmware/niusbFirebolt.cfg`

## 1. 结论一句话

FX3（Cypress CYUSB301x，ThreadX/ARM9）在 Firebolt / NI USB-6453 中承担
**USB 配置代理 + DMA 数据搬运桥**，**不是采集同步时基**。
采样节拍（convert / sample clock）位于 FPGA + ADC 层，ARM 核只做控制面转发与批量流搬运。

## 2. 静态证据（来自 `fx3_deep.json`）

| 证据 | 值 | 含义 |
|------|-----|------|
| CY 头 | magic `43 59 1c b0`（`CY` + ctrl `0x1c 0xb0`，exec marker `0xB0`）| 标准 Cypress FX3 启动镜像 |
| USB VID/PID | `0x3923` / `0x7B44`（bcdUSB `0x0210`，desc @283432）| 匹配 Firebolt / USB-6453 社区上报 |
| RTOS | ThreadX ARM9/RVDS `G5.1.5.1`，SN `2923-115-1301` | Express Logic 版权串 |
| 镜像大小 / 熵 | 361054 B，整体熵 5.814 | 典型固件（代码+表），非压缩/加密整体块 |
| 大零区 | 1 处：offset `0x50778`，长度 31400 B（占 8.7%）| flash 尾部填充 / 擦除区，非有效负载 |

### 内部源码树（`source/` 路径，共 11 条）

```
source/nimarengoSrc/main.c
source/nimarengoSrc/startup/tFPGA.c            # 加载/配置 FPGA
source/nimarengoSrc/tFPGARegisterAccess.c      # 读写 FPGA 寄存器（映射未知）
source/nimarengoCore/tDMAManager.c             # DMA 管理
source/nimarengoCore/tDescriptor.c
source/nimarengoCore/tScheduler.c
source/nimarengoCore/tTimer.c
source/nimarengoCore/fx3/tSerialFlash.c
source/nimarengoCore/fx3/tUart.c
source/nimarengoCore/fusion2/tFusionManager.c              # Fusion 控制路径
source/nimarengoCore/fusion2/tFusionVendorDeviceRequest.h  # Fusion 厂商请求
```

平台命名 `nimarengoCore / nimarengoSrc` = NI Marengo 平台。

### ThreadX 线程与处理器

- 线程（9）：`01_DMA_THREAD`、`02_SYSTEM_THREAD`、`03_PIB_THREAD`、
  `04_UIB_THREAD`、`05_LPP_THREAD`、`06_SIB_THREAD`、`07_DEBUG_THREAD`、
  `Main Thread`、`System Timer Thread`
- 处理器（3）：`42:Secondary IRQ handler`、`43:State Machine handler`、
  `45:Counter Data Monitor handler`
- Fusion/DMA/FPGA 锚点：`Fusion`（3）、DMA/PIB/`_dmaBuf`（4）、FPGA（2）

`PIB_THREAD`（Processor Interface Block）+ `tDMAManager.c` + `_dmaBuf` =
GPIF↔DMA 数据面；`tFPGA.c` + `tFPGARegisterAccess.c` = 上电配置 FPGA 并访问其寄存器；
`tFusionManager.c` + `tFusionVendorDeviceRequest.h` = USB 厂商请求控制面。
这些都属于「代理 + 搬运」职责，镜像中**没有**采样时钟/转换节拍引擎。

## 3. 与 `FX3-*` catalog 对照

对照 `catalogs/catalog_fx3.py`（本文档不修改该文件）：

| catalog 标识 | 状态 | 本次静态深挖是否复现 |
|------|------|------|
| `FX3-IMG-CY-MAGIC` | confirmed | ✅ `cy_header.magic_hex = 43591cb0` |
| `FX3-USB-VIDPID` | confirmed | ✅ `usb = 0x3923 / 0x7B44` |
| `FX3-RTOS-THREADX` | confirmed | ✅ ThreadX `G5.1.5.1` |
| `FX3-SRC-NIMARENGO` | confirmed | ✅ 11 条 `source/nimarengo*` 路径 |
| `FX3-FPGA-LOAD` | confirmed | ✅ `startup/tFPGA.c` |
| `FX3-FPGA-REGACC` | confirmed | ✅ `tFPGARegisterAccess.c`（映射内容仍未知） |
| `FX3-FUSION` | confirmed | ✅ `tFusionManager.c` / `tFusionVendorDeviceRequest.h` |
| `FX3-DMA` | confirmed | ✅ `01_DMA_THREAD` / `03_PIB_THREAD` / `tDMAManager.c` |
| `FX3-STATE-MACHINE` | hypothesis | ➖ 仅见 `43:State Machine handler` 字符串，语义未定（可能是 USB/设备状态机，非采样 FSM） |
| `FX3-COUNTER-MON` | candidate | ➖ 仅见 `45:Counter Data Monitor handler`，未证明与 AI 时钟关联 |
| `FX3-REGMAP` | unknown | ❌ 见下节升级手段 |
| `FX3-FUSION-REQ` | unknown | ❌ 见下节升级手段 |
| `FX3-ROLE-SUMMARY` | confirmed | ✅ 本文档结论：配置代理 + DMA 桥，非同步时基 |

## 4. unknown 项与升级手段（本阶段不执行抓包）

### `FX3-REGMAP` —— 具体 FPGA 寄存器偏移/位域

- 现状：只知道存在 `tFPGARegisterAccess.c`，**寄存器地址与位定义未知**。
- 升级手段（静态优先）：
  1. 用 Ghidra/IDA 载入本镜像（ARM9 Thumb），从 `tFPGARegisterAccess.c` 相关函数
     追常量地址与移位/掩码，重建寄存器映射。
  2. 交叉核对 FPGA 侧 `niusbFireboltFPGA.cfg`（见 `manifests/bitstream_meta.json`，
     XC7A100T）以印证寄存器窗口。
- 不做：本阶段不进行 USB/GPIF 抓包。

### `FX3-FUSION-REQ` —— Fusion bRequest / payload 字典

- 现状：控制路径存在（`tFusionManager.c` / `tFusionVendorDeviceRequest.h`），
  **具体 bRequest 码与负载结构未知**。
- 升级手段：
  1. Ghidra 反编译 `tFusionVendorDeviceRequest` 分发表，枚举 bRequest 分支。
  2. （显式推迟）USB 控制传输抓包，对照分支验证语义。
- 本阶段明确**不抓包**，保留为 `unknown`。

## 5. 边界声明

本文档只依据静态字节与可打印字符串。凡涉及**运行时行为、寄存器语义、
Fusion 请求语义、采样时钟树**，均标记为 `unknown`，需 Ghidra 反编译或
USB/逻辑抓包升级，且升级动作不在本阶段执行。
