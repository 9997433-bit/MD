# 六问书面答案（LEARN_ANSWERS）

> 对应 `LEARNING_GUIDE.md` 的六问验收。每问给出：结论、证据等级、引用 identifier；
> 凡 `unknown` 一律不升格，并指向 `OMISSIONS_AND_REMAINING.md` 的升级手段。
> 本文件仅为静态学习答卷，不声称厂商等价（见 `LEARN-NO-VENDOR-EQ`）。

---

## 问 1：同步在哪一层发生？

**结论**：多通道同步发生在**硬件层**——16 个物理 ADC 在共享 convert 时钟下同时转换，同步的落点是 ADC 阵列 + FPGA（Artix-7 XC7A100T）内的时钟/转换逻辑，而不是 FX3 ARM 固件的软件对齐，更不是主机侧对齐。FX3 固件字符串中没有 sample/sync 相关的时基角色，只承担配置与搬运。

**证据等级**：`confirmed`（同步层级本身）；但 FPGA 内部时钟树的**网表级连线**仍为 `unknown`。

**引用 identifier**：
- `SPEC-SYNC-LAYER`（confirmed，spec_derived）— 同步是 hardware convert-on-shared-clock，非主机软件对齐
- `SPEC-ADC-16` / `SPEC-SIM-MAX-16CH`（confirmed）— 16 物理 ADC、最多 16 路真同时
- `HW-SYNC-LOCUS`（confirmed，spec_plus_arch）— 同步落点为 ADC 阵列 + FPGA，非 FX3
- `BIT-SYNC-CLOCK-TREE`（unknown）— fabric 内的时钟树连线未证明

**unknown 升级**：`BIT-SYNC-CLOCK-TREE` → OMISSIONS「网表逆向或芯片级探测」。注意 forced null bridge：`SPEC-SIM -> BIT-SYNC-CLOCK-TREE proven wiring` 强制置空，不得越过。

---

## 问 2：16 路同时 vs 32 路单端 bank 的条件？

**结论**：设备有 16 个 ADC。全部 16 路差分（DIFF）、或单端（SE）通道不发生「同一 ADC 配对」冲突时，最多 16 路可真同时采样，达 1 MS/s/ch。SE 模式下 AIn 与 AIn+8 共享同一个 ADC（如 AI0 与 AI8）；当同一 ADC 的两个 SE 通道都被使用（即用到 32 SE 或跨 bank 配对）时，退化为 bank 扫描：先 AI0:7 再 AI8:15，速率降到 500 kS/s/ch，bank 间间隔由 AIConv.Rate 控制。

**证据等级**：`confirmed`（规格书原文层面）。

**引用 identifier**：
- `SPEC-SIM-MAX-16CH` / `SPEC-SIM-1MS`（confirmed）— 最多 16 路同时、1 MS/s/ch
- `SPEC-SE-PAIR`（confirmed）— AIn 与 AIn+8 共享一个 ADC
- `SPEC-BANK`（confirmed）— 同 ADC 双 SE 走 bank 扫描，500 kS/s/ch
- `SPEC-AICONV-RATE`（confirmed）— bank 间延迟由 AIConv.Rate 属性控制

**unknown 升级**：bank 切换的器件级实现见问 3/问 6（`BIT-BANK-AICONV`、`FX3-REGMAP`）。

---

## 问 3：Sample clock / Start trigger / AIConv 各管什么？

**结论**：三者语义分工（规格层面）：
- **Sample clock**：决定每个「样本时刻」的节拍，时基分辨率 10 ns、精度 50 ppm；同时采样场景下所有在用 ADC 在该节拍上共享 convert。
- **Start trigger**：决定采集任务**何时开始**，可由 PFI0:15 线输入/输出（PFI 可作为 AI 定时与触发的源/汇）。
- **AIConv（AIConv.Rate）**：仅在 bank 扫描场景生效，控制同一 sample 周期内两个 bank（AI0:7 → AI8:15）之间的转换间隔。它是 NI 软件属性名，对应的**器件寄存器未知**。

**证据等级**：`confirmed`（三者的软件/规格语义）；器件侧实现为 `unknown`。

**引用 identifier**：
- `SPEC-TIMING-RES`（confirmed）— 10 ns 分辨率 / 50 ppm
- `SPEC-PFI-TRIG`（confirmed）— PFI 线可源/汇 AI 定时与触发
- `SPEC-AICONV-RATE`（confirmed）+ `SPEC-BANK`（confirmed）— AIConv 控制 bank 间隔
- `BIT-BANK-AICONV`（unknown）— bank 切换与 AIConv 定时器 HDL 未证明
- `FX3-REGMAP`（unknown）— 对应寄存器偏移未还原
- 旁证边界：`FX3-COUNTER-MON` 仅为 `candidate`，且 forced null bridge `Counter-Data-Monitor -> AI sample clock identity` 禁止把它当作 AI sample clock 证据

**unknown 升级**：`BIT-BANK-AICONV` → OMISSIONS「网表逆向 / 实机 + 抓包对照」；`FX3-REGMAP` → OMISSIONS「Ghidra 深挖 + 抓包」。

---

## 问 4：FX3 与 FPGA 谁负责什么？

**结论**：
- **FX3（Cypress CYUSB3014，ThreadX ARM9 固件）**：USB 设备端点与 Fusion vendor 控制路径的承载者；FPGA 的**配置代理**（`startup/tFPGA.c` 加载/配置 FPGA）与**寄存器代写者**（`tFPGARegisterAccess.c`）；数据面上是 **DMA 桥**（DMA/PIB 线程把 GPIF 数据搬向 USB）。它**不是**同步时基。
- **FPGA（Artix-7 XC7A100T）**：按 SPEC+架构推断承载采样定时、多 ADC convert、bank/AIConv 定时与 AI FIFO 等实时逻辑——但这些均无网表级字节证据，只有「同步不在 FX3、必在 ADC+FPGA」的排除法结论。

**证据等级**：FX3 角色 `confirmed`（固件字符串 + 架构综合）；FPGA 承载具体同步/定时/FIFO 逻辑为 `unknown`（仅落点判断 confirmed）。

**引用 identifier**：
- `FX3-ROLE-SUMMARY`（confirmed，arch_synthesis）— FX3 = 配置代理 + DMA 桥，非同步时基
- `FX3-FPGA-LOAD` / `FX3-FPGA-REGACC` / `FX3-DMA` / `FX3-FUSION`（confirmed，firmware_string）
- `BIT-IDCODE` / `HW-FPGA-XC7A100T`（confirmed）— FPGA 器件身份
- `HW-SYNC-LOCUS`（confirmed）— 同步落点在 ADC+FPGA
- `BIT-SYNC-CLOCK-TREE` / `BIT-BANK-AICONV` / `BIT-FIFO-LOGIC`（unknown）— FPGA 内部职责的具体 HDL
- `FX3-STATE-MACHINE` 仅 `hypothesis`（可能是设备/USB 状态机而非 AI 采样 FSM），不得引为 AI 职责证据

**unknown 升级**：BIT-* 三项 → OMISSIONS「网表逆向 / 实机」；`FX3-REGMAP` → 「Ghidra + 抓包」。

---

## 问 5：FIFO→USB 帧如何打包？

**结论**：静态包只能证明到：AI 输入 FIFO 深 8191 samples 且由在用通道**共享**（非每通道独立）；高速数据路径走 USB Signal Stream；FX3 侧存在 DMA/PIB 线程与 Fusion 符号锚点。至于**帧内通道打包格式**（通道交织顺序、样本位宽/对齐、帧头/计数器等）——本阶段**无任何字节证据**，只能作为假设保留，不作陈述性结论。

**证据等级**：FIFO 深度与 Signal Stream 路径 `confirmed`；帧内打包格式 `unknown`（整体按 LEARN-Q5 要求只能停在 hypothesis/unknown）。

**引用 identifier**：
- `SPEC-FIFO-AI`（confirmed）— 8191 samples 共享 FIFO
- `SPEC-XFER-STREAM`（confirmed）— AI 数据走 USB Signal Stream
- `FX3-DMA`（confirmed）— DMA/PIB 线程存在（仅为路径锚点）
- `USB-FRAME-LAYOUT`（unknown，OMISSIONS 条目）— 帧内通道打包格式
- `BIT-FIFO-LOGIC`（unknown）— fabric 侧 FIFO/打包 HDL
- forced null bridges：`FX3-FUSION-SYMBOL -> USB-FRAME-LAYOUT`、`BIT-IDCODE -> channel packing format` 均强制置空

**unknown 升级**：`USB-FRAME-LAYOUT` → OMISSIONS「抓流 / 驱动静态」；`BIT-FIFO-LOGIC` → 「网表逆向」。

---

## 问 6：哪些结论必须抓包/实机/网表才能升级？

**结论**：以下条目在静态包内**不可能**升为 confirmed，必须按 OMISSIONS 登记的手段升级；升级前保持 unknown。

| identifier | 缺口 | 升级手段（OMISSIONS） |
|---|---|---|
| `BIT-SYNC-CLOCK-TREE` | FPGA 内 sample clock / convert 同源连线 | 网表逆向或芯片级探测 |
| `BIT-BANK-AICONV` | bank 切换与 AIConv 定时器 HDL | 网表逆向 / 实机 + 抓包对照 |
| `BIT-FIFO-LOGIC` | fabric 内 AI FIFO 尺寸/打包 HDL | 网表逆向 |
| `FX3-REGMAP` | `tFPGARegisterAccess` 寄存器偏移表 | Ghidra 深挖 + 抓包 |
| `FX3-FUSION-REQ` | Fusion vendor bRequest/payload 字典 | **USB 抓包**（本阶段刻意延后） |
| `USB-FRAME-LAYOUT` | Signal Stream 帧内通道打包格式 | 抓流 / 驱动静态 |
| `HW-ADC-MPN` | 16×ADC 确切料号 | 高清照片丝印 / 原理图（HW-PHOTO-LOCAL：照片拉取入库） |
| `HOST-DAQMX` | 主机 API→Fusion 映射 | 驱动/NI-DAQmx 静态（范围外） |

**证据等级**：本清单本身 `confirmed`（照抄 `OMISSIONS_AND_REMAINING.md` 与 `LEARN-Q6-UPGRADE-PATH`、`LEARN-NO-CAPTURE-YET` 登记）；表内各条目状态均为 `unknown`。

**引用 identifier**：`LEARN-Q6-UPGRADE-PATH`、`LEARN-NO-CAPTURE-YET`、`bridge_matrix.json → forced_null_bridges`（8 条强制置空桥在对应证据到位前一律保持 null）。

---

## 停止条件重申

目录与 catalog 齐全 **不等于** 掌握运行行为或可实现同卡功能驱动（`LEARN-NO-VENDOR-EQ`；`OMISSIONS_AND_REMAINING.md` 停止条件提醒）。
