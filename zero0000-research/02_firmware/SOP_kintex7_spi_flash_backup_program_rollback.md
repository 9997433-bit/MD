# Kintex-7 + SPI Flash 固件备份 / 烧录 / 回滚 SOP

| 项目 | 内容 |
| --- | --- |
| 适用平台 | Xilinx Kintex-7（XC7K 系列），配置模式 Master SPI |
| 配置存储器 | Spansion / Cypress（现 Infineon）S25FL128S，128 Mbit ≈ 16 MB |
| 目标固件 | `20230825_s2056.mcs`（仓库路径：`zero0000-research/assets/firmware/20230825_s2056.mcs`） |
| 固件 SHA256 | `dc91db8e4b80e0b6b971cf03e8b95e6eafc1905e390a80c1ba2625b5e67507c0` |
| 固件说明 | Intel HEX（MCS）格式，文本约 18.8 MB；有效数据自地址 `0x000000` 起，约 6.7 MB（终止于 `0x661EDB` 附近），远小于 16 MB Flash 容量 |
| 文档版本 | v1.0（2026-08-28） |

> **总原则：先备份、再校验、后烧录。任何一步没有把握，停下来，不要断电、不要拔线。**

---

## 1. 工具清单

### 1.1 硬件

| 工具 | 说明 |
| --- | --- |
| JTAG 下载器 | Xilinx Platform Cable USB II，或 Digilent HS1/HS2/HS3（板载 FTDI JTAG 亦可） |
| 目标板 | 确认 JTAG 座（通常 14-pin 2mm 或 6-pin）方向与 3.3V/2.5V VREF |
| 稳定供电 | 烧录期间禁止使用不可靠电源；有条件时接 UPS 或实验室直流源 |
| 防静电 | 接地手环、防静电垫 |

### 1.2 软件

| 工具 | 用途 | 备注 |
| --- | --- | --- |
| **Vivado Hardware Manager**（推荐 2018.3 及以上，Lab Edition 即可） | 备份、擦除、烧录 SPI Flash；JTAG 直接烧 bit | 主力工具，本 SOP 以它为准 |
| `program_flash`（随 SDK/Vitis 附带的命令行工具） | 命令行批量烧录 | 主要面向 Zynq，对纯 7 系列 + SPI 支持有限；**仅作备选**，失败请回到 Vivado |
| `hw_server` | JTAG 服务端（Vivado 自带，默认端口 3121） | 远程烧录时手动启动 |
| 校验工具 | `sha256sum` / `certutil -hashfile`（Windows） | 烧录前核对固件哈希 |

### 1.3 Flash 器件名（Vivado 内选择）

S25FL128S 有两种扇区结构，Vivado 中分别对应：

- `s25fl128sxxxxxx0-spi-x1_x2_x4`（256 KB 均匀扇区，料号尾缀 …0）
- `s25fl128sxxxxxx1-spi-x1_x2_x4`（64 KB 扇区，料号尾缀 …1）

**先看芯片丝印确认具体料号**（如 `S25FL128SAGMFI001` → 选尾缀 1 的条目）。若丝印不可读，先试其一，`Blank Check`/读 ID 报错再换另一个。选错型号是烧录失败最常见原因之一。

---

## 2. 烧录前备份（必做，不可跳过）

目的：把 Flash 里当前正在运行的旧固件完整读出并存档，作为回滚依据。

### 2.1 连接与识别

1. 目标板**断电**，接好 JTAG 线缆，再上电。
2. 打开 Vivado → `Flow` → `Open Hardware Manager` → `Open Target` → `Auto Connect`。
3. 确认器件列表出现 `xc7k…`（具体型号视板卡而定）。若识别不到，检查 JTAG 线序、VREF、板卡供电后重试。

### 2.2 挂载配置存储器

1. 右键 FPGA 器件 → `Add Configuration Memory Device…`。
2. 搜索 `s25fl128s`，按 §1.3 选择正确条目 → `OK`。
3. 弹出 "Do you want to program the configuration memory device now?" → **选 No**（先备份，不烧录）。

### 2.3 读回全片内容

GUI 操作：右键刚添加的 Flash 器件 → `Readback Configuration Memory Device…` → 输出文件填 `flash_backup_YYYYMMDD.bin`，格式 BIN，地址范围 `Entire Configuration Memory Device` → `OK`。全片 16 MB 读回约需数分钟。

等效 Tcl（Hardware Manager 的 Tcl Console 中执行）：

```tcl
# 已 Auto Connect 且已 Add Configuration Memory Device 后：
set cfgmem [current_hw_cfgmem]
set_property PROGRAM.ADDRESS_RANGE {entire_device} $cfgmem
readback_hw_cfgmem -format BIN -file {flash_backup_20260828.bin} $cfgmem
```

### 2.4 备份校验（关键）

1. **读两次**，比对两次读回文件哈希一致，排除线缆抖动导致的坏备份：

```bash
sha256sum flash_backup_a.bin flash_backup_b.bin   # 两个哈希必须相同
```

2. 用十六进制查看器确认文件开头能找到 Xilinx 同步字 `AA 99 55 66`（表明读到了有效 bitstream，而不是全 `FF`）。
3. 备份文件**至少存两处**（本机 + 仓库/NAS），命名含日期与板卡序列号，例如 `flash_backup_20260828_SN0007.bin`，并记录哈希。

> 两次读回哈希不一致 → 检查 JTAG 线缆/降 JTAG 时钟（`Open Target` 时把频率降到 6 MHz 以下）后重读。备份未确认可靠之前，**禁止进入第 3 步**。

---

## 3. 用 MCS 烧录 SPI Flash（标准流程）

### 3.1 烧录前检查清单

- [ ] §2 备份已完成且两次读回哈希一致
- [ ] 待烧文件哈希核对：`sha256sum 20230825_s2056.mcs` 应为 `dc91db8e…67507c0`（见文首表格）
- [ ] 供电稳定，操作期间无人会碰电源/线缆
- [ ] 确认该 mcs 与本板卡硬件版本匹配（管脚约束、Flash 电压域一致）

### 3.2 GUI 步骤

1. Hardware Manager 中右键 Flash 器件 → `Program Configuration Memory Device…`。
2. `Configuration file` 选 `20230825_s2056.mcs`。
3. 勾选：`Erase`、`Program`、`Verify`（**Verify 必须勾**）；`Blank Check` 可选（勾上更稳，但耗时增加）。
4. Address Range 选 `Configuration File Only`（只擦写文件覆盖的 ~6.7 MB，比全片快且减少无谓磨损）。
5. `OK`，等待流程走完。典型耗时：擦除+写入+校验共 3–10 分钟。**期间绝对不可断电或拔 JTAG。**
6. 日志中确认 `Flash programming completed successfully` 且 Verify 无报错。

等效 Tcl：

```tcl
set cfgmem [current_hw_cfgmem]
set_property PROGRAM.FILES {20230825_s2056.mcs} $cfgmem
set_property PROGRAM.ADDRESS_RANGE {use_file} $cfgmem
set_property PROGRAM.ERASE 1 $cfgmem
set_property PROGRAM.BLANK_CHECK 0 $cfgmem
set_property PROGRAM.CFG_PROGRAM 1 $cfgmem
set_property PROGRAM.VERIFY 1 $cfgmem
program_hw_cfgmem $cfgmem
```

### 3.3 烧后验证

1. Vivado 中右键 FPGA 器件 → `Boot from Configuration Memory Device`（等效于发脉冲到 PROGRAM_B），或直接给板卡**完整断电再上电**。
2. 观察 DONE 指示灯点亮（通常绿色），并做业务级功能自检（通信、指示灯、版本号读取等）。
3. 记录：日期、操作人、板卡序列号、烧录文件名与哈希、验证结果。

### 3.4 命令行备选：program_flash

仅在无法使用 Vivado GUI 时尝试（该工具对非 Zynq 平台支持有限）：

```bash
program_flash -f 20230825_s2056.mcs \
  -flash_type s25fl128sxxxxxx0-spi-x1_x2_x4 \
  -blank_check -verify \
  -cable type xilinx_tcf url TCP:127.0.0.1:3121
```

报错（如提示需要 FSBL 或不识别 flash_type）即放弃，回到 §3.2 的 Vivado 流程。

---

## 4. 应急方案：仅 JTAG 直接烧 bit（不动 Flash）

适用场景：需要临时验证某版本逻辑、Flash 烧录通道异常、或不确定新固件是否可用时先"试跑"。

**前提：需要 `.bit` 文件。** `.mcs` 不能直接经 JTAG 配置 FPGA。若只有 `20230825_s2056.mcs` 而无对应 `.bit`，需从原始 Vivado 工程重新 `write_bitstream` 生成，或向固件提供方索取同版本 bit。

步骤：

1. Hardware Manager → `Auto Connect`。
2. 右键 FPGA 器件 → `Program Device…` → 选择 `.bit` 文件 → `Program`。
3. DONE 灯亮即配置成功，逻辑立刻运行。

等效 Tcl：

```tcl
set_property PROGRAM.FILE {design.bit} [current_hw_device]
program_hw_devices [current_hw_device]
```

**注意事项：**

- JTAG 配置是**易失**的：断电或按 PROGRAM_B 后即丢失，下次上电仍从 SPI Flash 加载旧固件。这正是它作为"无风险试跑"手段的价值。
- 试跑通过后，再按 §3 把对应 mcs 写入 Flash 固化。
- JTAG 配置的优先级高于当前运行状态，但不影响 Flash 内容——任何时候用它都不会"越烧越坏"。

---

## 5. 变砖恢复路径

"变砖"在此定义为：上电后 DONE 不亮、业务不启动。**只要 JTAG 链路还能识别到 FPGA，就没有真砖，一定可救。**按下列顺序排查：

### 5.1 第一步：确认 JTAG 可达

板卡上电 → Hardware Manager `Auto Connect`。

- **能识别 `xc7k…`** → 进入 §5.2。Kintex-7 的 JTAG 端口独立于配置模式引脚（M[2:0]），无论 Flash 内容多坏，JTAG 始终可用。
- **不能识别** → 硬件层问题（供电、JTAG 线序、VREF、器件损坏），与固件无关，转硬件排查，不在本 SOP 范围。

### 5.2 第二步：JTAG 试跑已知好版本

按 §4 用 JTAG 烧一个**已知可用**的 `.bit`：

- 能跑起来 → 确认是 Flash 内容问题（烧坏/烧错/被中断），进入 §5.3。
- 跑不起来 → 电源时序或硬件问题，转硬件排查。

### 5.3 第三步：经 JTAG 重写 Flash（回滚）

Vivado 烧写 Flash 走的是"间接编程"：先经 JTAG 向 FPGA 加载一个内置的 flash 编程桥 bitstream，再透过 FPGA 访问 SPI Flash——因此**只要 §5.1 通过，Flash 永远可以重写**，此前 Flash 里是什么内容都无所谓。

回滚到旧固件：

1. 按 §2.2 重新 `Add Configuration Memory Device`。
2. `Program Configuration Memory Device…`，Configuration file 选**备份文件** `flash_backup_YYYYMMDD.bin`（格式选 BIN，起始地址 0），勾 `Erase / Program / Verify`，Address Range 选 `Entire Configuration Memory Device`（BIN 回滚建议全片，保证与备份逐字节一致）。
3. 完成后断电重启，DONE 灯亮、业务恢复即回滚成功。

若怀疑 Flash 内残留脏数据导致启动异常，可先全片擦除再写：右键 Flash 器件 → `Erase`，或 Tcl 中置 `PROGRAM.ERASE 1`、地址范围 `entire_device` 单独执行擦除。

### 5.4 上电即卡死、来不及连 JTAG 的特殊情况

个别坏固件会让 FPGA 配置后把 JTAG 相关电源域/复位拉死。处理办法：

- 上电时**持续拉低 PROGRAM_B**（或按住板上 PROG 按键），阻止 FPGA 从 Flash 加载，保持未配置状态，此时连 JTAG 重写 Flash。
- 若板卡引出了模式引脚跳线，把 M[2:0] 从 `001`（Master SPI）改为 `101`（JTAG only），上电后 FPGA 不会尝试读 Flash，再按 §5.3 重写，完成后恢复跳线。

### 5.5 最后手段

JTAG 完全不可达且排除线缆/供电问题 → 用外部编程器（如 Dediprog SF100/SF600）夹持或拆焊 SPI Flash 直接写入备份 BIN。需要焊接能力，仅由硬件工程师执行。

---

## 6. 风险清单

| # | 风险 | 后果 | 防范措施 |
| --- | --- | --- | --- |
| 1 | 擦除/写入过程中断电或拔线 | Flash 内容不完整，上电不启动（可按 §5 恢复） | 稳定供电；操作期间守在现场；不碰线缆 |
| 2 | 未做备份直接烧录 | 新固件有问题时**无法回滚** | §2 为强制步骤；备份未双读校验不得烧录 |
| 3 | Flash 型号选错（…xxx0 vs …xxx1，扇区结构不同） | 擦除边界错位，写入/校验失败或内容损坏 | 看芯片丝印确认料号；Blank Check/读 ID 验证 |
| 4 | mcs 与硬件版本不匹配（管脚/电压域不同的板卡混用） | 轻则不工作，重则 IO 电平冲突损坏硬件 | 烧录前核对文件哈希与板卡型号/批次对应关系 |
| 5 | 备份文件本身是坏的（读回时线缆抖动） | 回滚时写入坏数据 | 读两次比哈希；检查同步字 `AA995566` |
| 6 | 跳过 Verify | 写入位错未被发现，间歇性启动失败 | Verify 必选，不允许为省时间取消 |
| 7 | JTAG 时钟过高、线缆过长/接触不良 | 识别失败、校验随机报错 | 降 JTAG 频率至 ≤6 MHz；换短线；重插 |
| 8 | Flash 写保护（WP#/状态寄存器 BP 位）被使能 | 擦写静默失败或报错 | 烧前确认板上 WP 跳线；异常时读状态寄存器 |
| 9 | 用 `program_flash` 在纯 7 系列上强行操作 | 工具行为不可预期 | 首选 Vivado；program_flash 仅备选且失败即止 |
| 10 | 多板混线操作（备份 A 板、烧了 B 板） | 备份与板卡对不上，回滚失效 | 一次只接一块板；文件名带板卡序列号 |
| 11 | 静电损伤 | Flash/FPGA 永久损坏 | 手环接地；拿板卡持边缘 |
| 12 | JTAG 试跑版本被误认为已固化 | 断电后"固件丢失"的假象 | 明确记录：JTAG 烧 bit 是易失的，固化必须走 §3 |

---

## 附录：快速命令速查

```tcl
# —— Vivado Tcl 全流程（Hardware Manager Tcl Console）——
open_hw_manager
connect_hw_server
open_hw_target
current_hw_device [lindex [get_hw_devices xc7k*] 0]

# 挂载 Flash（按丝印选 …xxx0 或 …xxx1）
create_hw_cfgmem -hw_device [current_hw_device] \
    [lindex [get_cfgmem_parts {s25fl128sxxxxxx0-spi-x1_x2_x4}] 0]

# 备份（全片读回）
set_property PROGRAM.ADDRESS_RANGE {entire_device} [current_hw_cfgmem]
readback_hw_cfgmem -format BIN -file {flash_backup.bin} [current_hw_cfgmem]

# 烧录 mcs（擦除+写入+校验）
set_property PROGRAM.FILES {20230825_s2056.mcs} [current_hw_cfgmem]
set_property PROGRAM.ADDRESS_RANGE {use_file} [current_hw_cfgmem]
set_property PROGRAM.ERASE 1 [current_hw_cfgmem]
set_property PROGRAM.CFG_PROGRAM 1 [current_hw_cfgmem]
set_property PROGRAM.VERIFY 1 [current_hw_cfgmem]
program_hw_cfgmem [current_hw_cfgmem]

# 从 Flash 重启 FPGA
boot_hw_device [current_hw_device]

# 应急：JTAG 直接烧 bit（易失）
set_property PROGRAM.FILE {design.bit} [current_hw_device]
program_hw_devices [current_hw_device]
```
