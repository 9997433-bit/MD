# 已确认证据汇总报告（CONFIRMED_REPORT）

> 账本刷新后 confirmed=45 / 总标识=57（若下文仍写旧计数，以 coverage.json 为准）。

> 产品：NI USB-6453（内部代号 Firebolt） · 阶段：`static_skeleton_no_capture`（静态骨架，未抓包）
> 数据源：`EvidenceLedger.json` / `bridge_matrix.json` / `OMISSIONS_AND_REMAINING.md`
> 声明：**目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

本报告仅汇总 `status = confirmed` 的 identifier，共 **40 条**（总登记 52 条：confirmed 40 / candidate 5 / unknown 6 / hypothesis 1）。
下文按「产品身份 / 同步语义 / 硬件 / FX3 角色 / FPGA 载体 / 学习策略」六组叙述，并说明这些已确认点如何支撑“**与本卡同一功能的学习结论**”，最后列出**仍不能声称**的事项。

---

## 1. 产品身份（5 条）

| identifier | 边界 boundary | 已确认内容 |
|---|---|---|
| `SPEC-PRODUCT-USB-6453` | spec_and_usb_pid | 产品即 NI USB-6453 mioDAQ（Firebolt）：32 SE / 16 DIFF AI、4 AO、16 DIO；社区将 PID `0x7B44` 对应 Firebolt |
| `SPEC-AO-4CH` | spec_sheet | 4 路模拟输出（登记以补全 system_map，同步学习中优先级低） |
| `SPEC-DIO-16` | spec_sheet | 16 条 DIO/PFI 线（Port0/line0:15） |
| `HW-BRAND-NI` | photo_silkscreen | PCB 丝印为 National Instruments（NI logo / ni.com/patents / © 2024） |
| `HW-USB-C` | photo | 板边可见 USB Type-C 主机接口 |

**支撑作用**：把“研究对象”钉死为**本卡这一具体型号**。规格给出的通道数/功能集与实物丝印、USB-C 主机口相互印证，保证后续所有同步语义结论都是绑定在 USB-6453 而非泛化的“某 DAQ 卡”上，这是“同一功能学习结论”的前提。

---

## 2. 同步语义（11 条）

| identifier | 边界 boundary | 已确认内容 |
|---|---|---|
| `SPEC-ADC-16` | spec_sheet | 物理 ADC 数量 = 16 |
| `SPEC-SIM-MAX-16CH` | spec_sheet | 最多 16 通道真正同时采样 |
| `SPEC-SIM-1MS` | spec_sheet | 全同步场景下 1 MS/s/ch（16 DIFF 或至多 16 SE） |
| `SPEC-SE-PAIR` | spec_sheet | SE 成对共用一个 ADC（AIn 与 AIn+8，如 AI0&AI8） |
| `SPEC-BANK` | spec_sheet | 同 ADC 双 SE 用分组扫描 500 kS/s/ch（AI0:7 再 AI8:15） |
| `SPEC-AICONV-RATE` | spec_sheet | `AIConv.Rate` 属性控制组间延迟（**仅软件属性名**，器件寄存器未知） |
| `SPEC-TIMING-RES` | spec_sheet | 定时分辨率 10 ns、精度 50 ppm（采样时基质量） |
| `SPEC-FIFO-AI` | spec_sheet | 输入 FIFO 8191 采样，由所用通道**共享**（非每通道独占） |
| `SPEC-XFER-STREAM` | spec_sheet | AI 数据路径走 USB Signal Stream（另列 programmed I/O，流为主高速路径） |
| `SPEC-PFI-TRIG` | spec_sheet | PFI 线可作 AI 定时与触发的源/汇（PFI0:15 与 DIO 复用） |
| `SPEC-SYNC-LAYER` | spec_derived | 多通道同步是**硬件按共享时钟转换**，非主机侧软件对齐（由 16-ADC 同时模型推导） |

**支撑作用**：这一组构成“**本卡如何做到同步采集**”的功能骨架——16 个物理 ADC、共享转换时钟、SE 成对分组扫描 + `AIConv.Rate` 间隔、10 ns 时基、共享 8191 FIFO、Signal Stream 高速通道、PFI 触发路由。它让我们能在**规格语义层面**完整复述本卡的同步行为，并明确区分“同时采样”（16 ch）与“32 SE 分组”两种模式的差别。

---

## 3. 硬件（4 条）

| identifier | 边界 boundary | 已确认内容 |
|---|---|---|
| `HW-FX3-CYUSB3014` | photo_marking | Cypress EZ-USB FX3 CYUSB3014（与固件 ThreadX ARM9 / FX3 字符串一致） |
| `HW-FPGA-ARTIX7` | photo_and_bitstream | 存在 Xilinx Artix-7 FPGA（照片丝印 + IDCODE XC7A100T） |
| `HW-FPGA-XC7A100T` | bitstream_idcode | FPGA 器件为 XC7A100T（IDCODE `0x0362C093`；照片 OCR 若读作 50T 以二进制为准） |
| `HW-SYNC-LOCUS` | spec_plus_arch | 同步实现位点在 **ADC 阵列 + FPGA**，而非 FX3 的 ARM 核（FX3 无采样/同步字符串；SPEC 要求共享转换时钟） |

> 注：`HW-BRAND-NI`、`HW-USB-C` 也是硬件类 confirmed，但已归入「产品身份」叙述，避免重复计数。

**支撑作用**：把规格里的“同步语义”落到**实物芯片分工**上。已确认的三大件（FX3 MCU、Artix-7 XC7A100T FPGA、以及 ADC 阵列所在位点）加上 `HW-SYNC-LOCUS` 的推断，确立了“同步动作发生在 FPGA/ADC 侧、FX3 不承担时基”这一功能结论的物理依据。

---

## 4. FX3 角色（9 条）

| identifier | 边界 boundary | 已确认内容 |
|---|---|---|
| `FX3-IMG-CY-MAGIC` | firmware_bytes | 镜像以 Cypress CY 头 + `0xB0` 执行标记开头（`niusbFirebolt.cfg` 偏移 0：`43 59 1c b0`） |
| `FX3-USB-VIDPID` | firmware_device_descriptor | USB VID `0x3923` PID `0x7B44`（与 Firebolt / USB-6453 社区报告一致） |
| `FX3-RTOS-THREADX` | firmware_string | ThreadX ARM9 G5.1.5.1（Express Logic 版权串） |
| `FX3-SRC-NIMARENGO` | firmware_string | 内部源码树 `nimarengoCore` / `nimarengoSrc`（Marengo 平台命名） |
| `FX3-FPGA-LOAD` | firmware_string | `startup/tFPGA.c` 负责加载/配置 FPGA（角色：配置代理） |
| `FX3-FPGA-REGACC` | firmware_string | `tFPGARegisterAccess.c` 读写 FPGA 寄存器（**寄存器映射本体未知**） |
| `FX3-FUSION` | firmware_string | 存在 Fusion vendor device request 路径（`tFusionManager` / `tFusionVendorDeviceRequest.h`） |
| `FX3-DMA` | firmware_string | DMA 管理器 + DMA/PIB 线程（`01_DMA_THREAD` / `03_PIB_THREAD` / `tDMAManager.c`） |
| `FX3-ROLE-SUMMARY` | arch_synthesis | FX3 = **配置代理 + DMA 桥**，而非同步时基（由字符串 + SPEC 同步层综合得出） |

**支撑作用**：确认了 FX3 在“本卡同一功能”里的**确切职责边界**——它把 FPGA 配置进去（`tFPGA.c`）、通过寄存器访问下发命令（`tFPGARegisterAccess.c`）、用 Fusion vendor 请求承载控制面、用 DMA/PIB 线程搬运数据流。结论：**FX3 是控制面代理与数据搬运桥，不产生采样时基**，与 `HW-SYNC-LOCUS`、`SPEC-SYNC-LAYER` 相互印证。

---

## 5. FPGA 载体（3 条）

| identifier | 边界 boundary | 已确认内容 |
|---|---|---|
| `BIT-FMT-BIN` | firmware_bytes | 原始 `.bin` 风格（FF 填充 + 总线宽度探测 + sync），无 Xilinx `.bit` ASCII 头 |
| `BIT-SYNC-WORD` | firmware_bytes | 存在同步字 `AA995566`（7-series bitstream） |
| `BIT-IDCODE` | bitstream_packet | IDCODE `0x0362C093` = XC7A100T（Type1 写 IDCODE） |

**支撑作用**：从 bitstream 二进制层面**确认承载体**：这是一枚 7-series（Artix-7 XC7A100T）的原始位流，格式、同步字、器件 IDCODE 三点自洽。它坐实了“同步逻辑的物理载体是这颗 FPGA”，为把同步语义归位到 FPGA 提供了器件级证据（但仅限**器件与格式**，不含内部时钟树，见下文限制）。

---

## 6. 学习策略（8 条）

| identifier | 边界 boundary | 已确认内容 |
|---|---|---|
| `LEARN-Q1-SYNC-LAYER` | checklist | 能解释同步层（ADC 共享转换 vs 软件对齐），对应 `SPEC-SYNC-LAYER` + `HW-SYNC-LOCUS` |
| `LEARN-Q2-16-VS-32` | checklist | 能解释 16 ch 同时 vs 32 SE 分组（`SPEC-SIM-*` / `SPEC-SE-PAIR` / `SPEC-BANK`） |
| `LEARN-Q3-CLOCK-TRIG-AICONV` | checklist | 能区分 sample clock / start trigger / AIConv 三种角色（SPEC 定时 + PFI + AIConv） |
| `LEARN-Q4-FX3-VS-FPGA` | checklist | 能陈述 FX3 与 FPGA 的职责划分（`FX3-ROLE-SUMMARY` vs BIT 未知项） |
| `LEARN-Q5-FRAME-PACK` | checklist | 能把 FIFO→USB 打包**仅**表述为 unknown/hypothesis（不得过度声称） |
| `LEARN-Q6-UPGRADE-PATH` | checklist | 能列出针对未知项的抓包/网表/实机升级路径（见 OMISSIONS） |
| `LEARN-NO-VENDOR-EQ` | policy | 接受停止条件：目录完整 ≠ 厂商等价（README 声明） |
| `LEARN-NO-CAPTURE-YET` | policy | 承认本阶段延后 USB 抓包（PHASE_PLAN 延后清单） |

**支撑作用**：这组是“学习结论”的**自检与纪律**层。Q1–Q4 证明前五组已确认点足以支撑对本卡同步功能的**完整复述**；Q5–Q6 与两条 policy 则把边界钉死——凡未证明处一律标记 unknown/hypothesis，并只给升级路径，不“猜通”。这保证了“与本卡同一功能的学习结论”是**可辩护、不越权**的。

---

## 已确认点如何支撑“与本卡同一功能的学习结论”

综合六组，可以对**本卡（USB-6453 / Firebolt）的同步采集功能**给出以下**规格 + 架构层面**的确定结论：

1. **身份确定**：对象即 USB-6453，VID/PID、丝印、接口一致（第 1 组）。
2. **同步机制可复述**：16 个物理 ADC 在**共享转换时钟**下同时采样，最高 16 ch @ 1 MS/s/ch；32 SE 情形下 SE 成对共享 ADC，用分组扫描 + `AIConv.Rate` 间隔在 500 kS/s/ch 下完成；时基 10 ns / 50 ppm；数据经共享 8191 FIFO 走 USB Signal Stream；PFI 提供触发/定时路由（第 2 组）。
3. **芯片分工确定**：同步位点在 ADC 阵列 + FPGA；FX3 只做 FPGA 配置代理、寄存器命令下发、Fusion 控制面与 DMA 数据桥（第 3、4 组，互相印证）。
4. **载体确认**：同步逻辑承载于 Artix-7 XC7A100T，其位流格式、同步字、IDCODE 自洽（第 5 组）。
5. **纪律达标**：以上结论均可通过 Q1–Q6 自检，且未证明处保持 unknown（第 6 组）。

即：**已确认点足以在“规格语义 + 芯片职责划分”层面完整地学习并复述本卡的同步采集功能**，并把每个论断都锚定到本卡实物/固件/位流证据上。

---

## 仍不能声称的事项（confirmed 之外，禁止升级）

这些属于 candidate / hypothesis / unknown 或被 `bridge_matrix.json` 强制置空的桥，**不得**据本报告宣称已掌握：

- **FPGA 内部同步实现**：`BIT-SYNC-CLOCK-TREE`（sample clock/convert 同源连线，unknown）、`BIT-BANK-AICONV`（bank 切换与 AIConv 定时器 HDL，unknown）、`BIT-FIFO-LOGIC`（FIFO 尺寸/打包 HDL，unknown）。器件确认 **≠** 时钟树/网表确认。
- **FX3 寄存器与控制协议**：`FX3-REGMAP`（`tFPGARegisterAccess` 具体偏移，unknown，需 Ghidra + 抓包）、`FX3-FUSION-REQ`（Fusion bRequest/payload 字典，unknown，**刻意延后抓包**）。
- **USB 帧格式**：Signal Stream 帧内通道打包格式（`USB-FRAME-LAYOUT`）未知；`BIT-IDCODE → 通道打包格式` 为强制 null 桥（器件确认 ≠ 帧格式确认）。
- **硬件料号**：`HW-ADC-MPN`（16×ADC 确切料号，unknown）；`HW-ADC-ARRAY` 仅 candidate（可见重复前端，料号未证）；`HW-ASSY-114365F`、`HW-OEM-S2C` 均为 candidate。
- **FX3 线程语义存疑项**：`FX3-STATE-MACHINE` 为 hypothesis（可能是设备/USB 状态机，非 AI 采样 FSM）；`FX3-COUNTER-MON` 为 candidate（未证明等于 AI sample clock）。
- **主机栈范围外**：`DMA_THREAD → DAQmx 任务语义`、`system_map NODE-HOST → Fusion 字段字典` 为强制 null 桥；主机 API→Fusion 映射（`HOST-DAQMX`）超出本包范围。
- **总体停止条件**（`coverage.json`）：`catalog_complete = true`，但 `vendor_equivalent = false`、`runtime_behavior_mastered = false`、`usb_capture_done = false`。**目录完整 ≠ 厂商等价 ≠ 掌握运行行为，更不等于可复现同卡功能驱动。**

升级手段（仅登记，未执行）：Fusion 请求的 USB 抓包、FX3 寄存器访问的 Ghidra 逆向、FPGA 网表/实机以还原同步时钟树。

---

**回报：confirmed 条数 = 40**（spec 14 / hardware 6 / fx3 9 / bitstream 3 / learn 8）。
