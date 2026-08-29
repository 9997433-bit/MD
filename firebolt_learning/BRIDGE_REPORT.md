# Bridge 报告（静态学习）

读取 `bridge_matrix.json`。强制 null 桥**不得**在无新证据时写通。

## 强制 null 为何必须保持

| 桥 | 原因 |
|----|------|
| SPEC-SIM → BIT-SYNC-CLOCK-TREE | 规格只证明“应同源 convert”；bitstream 元数据无网表连线 |
| SPEC-BANK → FX3-REGMAP AIConv | `AIConv.Rate` 是软件属性名，不是已还原的寄存器 |
| FX3-FUSION-SYMBOL → USB-FRAME-LAYOUT | 有 Fusion/DMA 符号 ≠ 知道 Signal Stream 帧布局 |
| BIT-IDCODE → channel packing | 器件确认 ≠ 通道打包格式 |
| HW-PHOTO-ADC-ARRAY → ADC MPN | 阵列可见 ≠ 料号可读 |
| DMA_THREAD → DAQmx semantics | 主机栈明确 out of scope |
| Counter-Data-Monitor → AI sample clock | 线程名旁证不足 |
| NODE-HOST → Fusion field dictionary | HOST=`not_started`；抓包延后 |

## cells 解读

各 `proven_bridge: null` 格子重复同一纪律：规格/照片/符号可支撑**学习语义与职责划分**，不能支撑**实现级字典**。

## 断桥仍能学什么

- 16 ADC 同时 vs bank 语义（SPEC）
- 同步 locus = ADC+FPGA（SPEC+架构）
- FX3 = 配置代理 + DMA 桥（固件字符串）

## 何时允许打破 null

仅当出现对应证据：网表/实机示波器、Ghidra 寄存器表、USB 抓包字段表、清晰丝印 BOM。升级前改 `bridge_matrix.json` 并跑 `make verify`。
