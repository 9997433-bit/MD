# USB-6453 / Firebolt 同步采集规格模型

> 阶段 B 文档。只登记规格语义，不推断 FPGA/FX3 寄存器实现。  
> **目录完整 ≠ 厂商等价 ≠ 掌握运行行为**

## 1. 规格钉死的硬件事实

| 概念 | 规格要点 | Catalog |
|------|----------|---------|
| ADC 数量 | 16 颗物理 ADC | `SPEC-ADC-16` |
| 真正同时 | 最多 16 路 simultaneous | `SPEC-SIM-MAX-16CH` |
| 满速 | 16 DIFF 或 ≤16 SE：1 MS/s/ch | `SPEC-SIM-1MS` |
| SE 成对 | AI*n* 与 AI*n+8* 共用同一 ADC | `SPEC-SE-PAIR` |
| Bank 扫描 | 同 ADC 两路都采 → 先 AI0:7 再 AI8:15，500 kS/s/ch | `SPEC-BANK` |
| 银行间隔 | `AIConv.Rate` 控制 | `SPEC-AICONV-RATE` |
| 时基 | 分辨率 10 ns，精度 50 ppm | `SPEC-TIMING-RES` |
| FIFO | Input FIFO 8191 samples，通道间共享 | `SPEC-FIFO-AI` |
| 传输 | USB Signal Stream（及 programmed I/O） | `SPEC-XFER-STREAM` |
| 触发/时钟 I/O | PFI0:15 可作 AI 定时/触发 | `SPEC-PFI-TRIG` |

## 2. 同步语义（核心结论）

**多通道“同步”= 多颗 ADC 在同一 sample clock 边沿上同时 convert**（`SPEC-SYNC-LAYER`）。  
不是主机收到数据后再做软件时间对齐。

32 路单端且同 ADC 两路都启用时，同步退化为 **bank 内同时 + bank 间 AIConv 延迟**，不再是 32 路严格同一瞬间。

## 3. 文字版状态机

```
[Idle]
  → 配置通道拓扑（DIFF16 / SE≤16 / SE32+bank）
  → 选择 Sample Clock（板内 timebase 或 PFI）
  → （若 bank）配置 AIConv.Rate
  → Arm
  → 等待 Start Trigger（软件 / PFI / 其它）
  → Running：各 ADC convert → 写入共享 FIFO
  → USB Signal Stream 上送
  → Stop / Error → Idle
```

详细 Mermaid 见 `docs/sync_state_machine.md`（并行产物）。

## 4. 与固件包的边界

| 层 | 规格模型回答什么 | 固件还需什么 |
|----|------------------|--------------|
| 同步是否发生 | 是，在 ADC+时钟 | FPGA 时钟树网表（unknown） |
| bank 行为 | 语义与速率上限 | AIConv 寄存器（unknown，需抓包/RE） |
| 谁搬数 | Signal Stream | FX3 DMA/Fusion 字段 |

## 5. 声明

本文件只服务学习结论；**不**等于可实现与厂商等价的驱动或比特流。
