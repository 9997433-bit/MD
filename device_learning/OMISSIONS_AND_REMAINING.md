# 遗漏登记与剩余边界（device_learning）

**更新时间**：2026-08-27  
**对象**：FPGA 器件静态学习包（配置比特流 + 硬件照片 + 附件目录）  
**器件事实**：Spartan-3 家族 `3s200ft256`，NCD 设计名 `TopUsb4431`，构建日期 2011/06/10（取自 `.bit` 头，非厂商机密）

本文档列出 **已知覆盖**、**建议后续补（candidate）**、**明确不做（unknown/forbidden）** 三类内容，并登记全部 missing/unknown 项及原因，供写作与下一步对照。

---

## 一、当前已知覆盖（有冻结证据）

| 类别 | 位置 | 状态 |
|------|------|------|
| 配置比特流头字段（设计名/器件/日期/UserID） | `firmware/device.bit` 头部 | 已读取 |
| 硬件外观照片 | `hardware/photos/*.jpg` | 已归档 |
| 强制 null 桥矩阵 | `bridge_matrix.json` | 已冻结（10 条） |

---

## 二、建议后续补（candidate，非阻塞）

| 类别 | 说明 | 缺口原因 |
|------|------|----------|
| 配置帧结构解析 | 从 `.bit` 提取帧地址/长度分区 | 需比特流格式表，尚无解析脚本 |
| 引脚清单 | FT256 封装引脚 → 功能表 | 无约束文件（UCF/PCF），照片不足以定位 |
| USB 端点枚举 | 端点数量/方向/包大小 | 未做在线抓包 |
| 时钟树 | 主时钟频率与分频 | 未从帧或在板测量确认 |
| 继电器/IO 通道数 | 照片可见连接器，未计数标注 | 分辨率与遮挡，缺电测 |

---

## 三、明确不做（保持 unknown / forbidden）

### 函数体 / 逻辑（unknown，禁止升级）

- `RTL-UNK-TOP-BODY` — 顶层设计 RTL 源不可得，禁止由比特流反推模块
- `RTL-UNK-LUT-EQUATION` — LUT init 未解码为布尔方程
- `RTL-UNK-BRAM-CONTENT` — BRAM 初始化内容未提取
- `FW-UNK-USB-FSM` — USB 控制状态机行为未知

### 无对应关系（missing，缺证据）

| identifier | 缺失项 | 原因 |
|------------|--------|------|
| `HW-MISS-PIN-MAP` | 引脚 → 功能映射 | 无约束文件锚点 |
| `HW-MISS-SCHEMATIC` | 原理图网络 | 仅有外观照片 |
| `USB-MISS-CMD-TABLE` | USB 命令码表 | 无主机侧抓包 |
| `USB-MISS-DRIVER-IOCTL` | 驱动 IOCTL 表 | 无驱动样本与动态跟踪 |
| `HW-MISS-EEPROM` | 配置存储内容 | 未转储 |

### 强制 null 桥（10 条，`proven_bridge` 永为 null）

见 `bridge_matrix.json`：

1. `bitstream_frame -> verilog_module`
2. `usb_command -> fpga_register`
3. `photo_trace -> pin_constraint`
4. `iob_pin -> relay_control_bit`
5. `lut_init -> boolean_function`
6. `clock_net -> timing_constraint`
7. `eeprom_descriptor -> usb_enumeration`
8. `config_frame -> block_ram_content`
9. `host_ioctl -> usb_command`
10. `photo_component -> schematic_net`

### forbidden（禁止行为）

- 禁止将比特流反编译为可综合源码后冒充原设计
- 禁止把照片推断的走线当作已证明的电气连接

---

## 四、动态层（下一步，不在静态包范围）

1. 在线 USB 抓包 → 建立命令码到寄存器写入的证据链
2. 万用表/逻辑分析仪确认 I/O 引脚 → 继电器控制位对应
3. 比特流帧解析工具链，尝试还原 LUT/BRAM 初始化

---

## 五、停止条件

| # | 条件 | 结果 |
|---|------|------|
| 1 | 目录内无空 identifier | 通过 |
| 2 | 无证据项保持 unknown/missing | 通过 |
| 3 | 强制 null 桥登记齐全 | 通过（10 条） |
| 4 | 无凭推测的层间映射被升级 | 通过 |

**声明**：静态可见 ≠ 掌握内部逻辑 ≠ 等价原设计。RTL 逻辑、LUT/BRAM 内容、USB 状态机保持 `unknown`。
